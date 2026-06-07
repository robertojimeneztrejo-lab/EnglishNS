import streamlit as st
from google import genai


class GeminiClientError(Exception):
    pass


@st.cache_resource
def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        raise GeminiClientError(
            "Falta GEMINI_API_KEY. Agrega tu clave en .streamlit/secrets.toml o en los Secrets de Streamlit Cloud."
        )
    return genai.Client(api_key=api_key)


def get_model_name() -> str:
    return st.secrets.get("GEMINI_MODEL", "gemini-2.5-flash")


def generate_text(prompt: str, temperature: float = 0.7) -> str:
    try:
        client = get_client()
        response = client.models.generate_content(
            model=get_model_name(),
            contents=prompt,
        )
        return getattr(response, "text", "") or "No recibí respuesta del modelo. Intenta de nuevo."
    except GeminiClientError:
        raise
    except Exception as exc:
        raise GeminiClientError(f"Error al consultar Gemini: {exc}") from exc
