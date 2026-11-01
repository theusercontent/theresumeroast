# The Workbench

A focused AI productivity suite built with Python and Streamlit. Bring your own OpenAI API key and use three tools from one workspace:

- **Resume Roaster** extracts text from a PDF and provides a role-specific critique and three actionable improvements.
- **Video to Blog** turns an accessible English YouTube transcript into a structured, SEO-friendly blog draft.
- **Regex Generator** creates a pattern, a short explanation, and example test cases for your chosen regex flavor.

## Get started

You'll need Python 3.10 or newer and an OpenAI API key with access to `gpt-4o-mini` and an active billing arrangement.

### Windows: one-click launcher

Download and extract the entire repository, then double-click **`run.bat`**. On first run, it creates a virtual environment and installs the dependencies; subsequent runs check them for updates. An internet connection is required for setup. The app should open in your browser; otherwise, open the Local URL shown in the launcher window. Keep that window open while using the app, and press Ctrl+C to stop it.

If Python is not installed, get it from [python.org](https://www.python.org/downloads/) and select **Add Python to PATH** during installation. You'll still need to enter your own OpenAI API key in the app.

### Manual setup (all platforms)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open the URL Streamlit prints in your browser. Enter your own OpenAI key in the sidebar, select a tool, and generate a result. Results can be downloaded as Markdown. Use the **Dark mode** switch in the sidebar to change the appearance for your current session. Your OpenAI account is responsible for the API usage charges.

## Privacy and limitations

- The app does not intentionally save API keys, uploaded files, transcripts, or results to disk. The key and results live in Streamlit session memory while the session is active; they are handled by the server running the app. If you deploy this for others, secure the server and use HTTPS. Streamlit's upload handling and hosting infrastructure may have their own retention policies.
- Resume text, transcripts, regex requirements and the key are sent to OpenAI to fulfill requests. YouTube transcript retrieval contacts YouTube. Review those providers' policies and avoid entering sensitive data you don't want to share. The app is not designed as a compliance or secure document storage solution.
- PDFs must be unlocked and contain selectable text; image-only scans aren't supported. Uploads are limited to 10 MB and source text to 60,000 characters.
- Videos need an accessible English transcript. YouTube may block requests, especially from cloud-hosted IP addresses. Private videos and videos without transcripts won't work.
- AI-generated content can be incorrect. Verify resume suggestions and blog claims; test generated regex patterns in the intended environment before use. Do not assume generated regex is safe against all inputs.

## Development

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

`app.py` contains the interface; `toolkit/core.py` handles validation, extraction, and prompts; `toolkit/llm.py` contains the OpenAI integration. No API key is required to run the unit tests.
