from __future__ import annotations

import logging
import google.generativeai as genai
from typing import Optional

from app.config import get_settings

logger = logging.getLogger("gemini")

class GeminiService:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.GEMINI_API_KEY
        self.model = None
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. GeminiService will be disabled.")
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")

    async def generate_mood_summary(self, country_name: str, headlines: list[str], mood_label: str) -> Optional[str]:
        """
        Generates a short summary explaining the mood based on headlines.
        """
        if not self.model or not headlines:
            return None

        # Prepare prompt
        headlines_text = "\n".join([f"- {h}" for h in headlines])
        prompt = (
            f"Here are the top news headlines for {country_name}:\n"
            f"{headlines_text}\n\n"
            f"The calculated mood for the country is '{mood_label}'.\n"
            f"Based on these headlines, write a 1-2 sentence summary explaining why the mood might be '{mood_label}'. "
            f"Keep it concise and analytical. Do not mention that you are an AI."
        )

        try:
            # Run in executor to avoid blocking async loop since genai might be synchronous
            import asyncio
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, self.model.generate_content, prompt)
            
            if response.text:
                return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating summary for {country_name}: {e}")
            
        return None
