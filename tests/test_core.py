import unittest
from unittest.mock import MagicMock, patch

from toolkit.core import (
    InputError, MAX_PDF_BYTES, MAX_SOURCE_CHARS, build_resume_prompt,
    extract_pdf_text, fetch_transcript, youtube_video_id,
)


class VideoIdTests(unittest.TestCase):
    def test_supported_urls(self):
        for url in ["dQw4w9WgXcQ", "https://youtu.be/dQw4w9WgXcQ?t=2", "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=x", "https://youtube.com/shorts/dQw4w9WgXcQ", "https://youtube.com/embed/dQw4w9WgXcQ", "https://youtube.com/live/dQw4w9WgXcQ"]:
            with self.subTest(url=url):
                self.assertEqual(youtube_video_id(url), "dQw4w9WgXcQ")

    def test_invalid_urls(self):
        for url in ["", "https://youtube.com.evil.test/watch?v=dQw4w9WgXcQ", "ftp://youtube.com/watch?v=dQw4w9WgXcQ", "https://youtu.be/notvalid", "https://youtube.com/playlist?list=abc"]:
            with self.subTest(url=url), self.assertRaises(InputError):
                youtube_video_id(url)


class PDFTests(unittest.TestCase):
    def test_invalid_files(self):
        for data in [b"", b"not a pdf", b"x" * (MAX_PDF_BYTES + 1)]:
            with self.subTest(length=len(data)), self.assertRaises(InputError):
                extract_pdf_text(data)

    @patch("toolkit.core.PdfReader")
    def test_extracts_and_rejects_empty_or_encrypted(self, reader):
        doc = reader.return_value
        doc.is_encrypted = False
        doc.pages = [MagicMock(extract_text=lambda: "Relevant experience")]
        self.assertEqual(extract_pdf_text(b"pdf"), "Relevant experience")
        doc.pages = [MagicMock(extract_text=lambda: "")]
        with self.assertRaises(InputError):
            extract_pdf_text(b"pdf")
        doc.is_encrypted = True
        with self.assertRaises(InputError):
            extract_pdf_text(b"pdf")

    @patch("toolkit.core.PdfReader")
    def test_long_resume_rejected(self, reader):
        reader.return_value.is_encrypted = False
        reader.return_value.pages = [MagicMock(extract_text=lambda: "x" * (MAX_SOURCE_CHARS + 1))]
        with self.assertRaises(InputError):
            extract_pdf_text(b"pdf")


class TranscriptTests(unittest.TestCase):
    @patch("youtube_transcript_api.YouTubeTranscriptApi")
    def test_fetch(self, api):
        api.return_value.fetch.return_value = [MagicMock(text="Hello"), MagicMock(text="world")]
        self.assertEqual(fetch_transcript("dQw4w9WgXcQ"), "Hello world")
        api.return_value.fetch.assert_called_once_with("dQw4w9WgXcQ")

    @patch("youtube_transcript_api.YouTubeTranscriptApi")
    def test_failure_is_safe(self, api):
        api.return_value.fetch.side_effect = RuntimeError("private internal details")
        with self.assertRaises(InputError) as exc:
            fetch_transcript("dQw4w9WgXcQ")
        self.assertNotIn("private internal details", str(exc.exception))


class PromptTests(unittest.TestCase):
    def test_resume_prompt_has_context_and_safety(self):
        system, user = build_resume_prompt("Python developer", "Engineer", "Balanced")
        self.assertIn("untrusted", system)
        self.assertIn("Engineer", user)
        self.assertIn("Python developer", user)


if __name__ == "__main__":
    unittest.main()
