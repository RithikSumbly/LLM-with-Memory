import os
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

import config

root = Path(__file__).resolve().parent.parent
load_dotenv(root / ".env")


class GeminiProvider:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not set. Copy .env.example to .env and add your key."
            )
        genai.configure(api_key=api_key)
        self._model = self._load_model(config.GEMINI_MODEL)

    def _load_model(self, model_name: str):
        return genai.GenerativeModel(model_name)

    def generate(self, prompt: str, system_instruction: str | None = None) -> str:
        try:
            if system_instruction:
                model = genai.GenerativeModel(
                    config.GEMINI_MODEL,
                    system_instruction=system_instruction,
                )
            else:
                model = self._model
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            if system_instruction:
                model = genai.GenerativeModel(
                    config.GEMINI_FALLBACK_MODEL,
                    system_instruction=system_instruction,
                )
            else:
                model = genai.GenerativeModel(config.GEMINI_FALLBACK_MODEL)
            response = model.generate_content(prompt)
            return response.text.strip()
