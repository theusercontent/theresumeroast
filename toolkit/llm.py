"""OpenAI boundary. No API keys or source content are logged here."""
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError, APITimeoutError, APIError


class GenerationError(Exception):
    pass


def generate(api_key: str, system: str, user: str) -> str:
    try:
        client = OpenAI(api_key=api_key, timeout=60, max_retries=1)
        result = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_tokens=1800,
        )
        content = result.choices[0].message.content
        if not content or not content.strip():
            raise GenerationError("The model returned an empty response. Please try again.")
        return content.strip()
    except AuthenticationError as exc:
        raise GenerationError("OpenAI rejected this API key. Check the key and try again.") from exc
    except RateLimitError as exc:
        raise GenerationError("OpenAI rate limit or quota reached. Check your usage and billing, then try again.") from exc
    except (APIConnectionError, APITimeoutError) as exc:
        raise GenerationError("Could not connect to OpenAI. Check your connection and try again.") from exc
    except APIError as exc:
        raise GenerationError("OpenAI couldn't complete the request. Please try again later.") from exc
