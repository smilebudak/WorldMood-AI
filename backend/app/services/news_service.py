"""
NewsService – fetches country headlines from Google News RSS and uses
Gemini AI to analyze sentiment.  The sentiment score (-1.0 … 1.0) is
blended into the mood engine alongside music features.
"""

from __future__ import annotations

import logging
import re
import asyncio
from typing import Optional
from xml.etree import ElementTree

import httpx
import numpy as np

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Google News RSS by country (uses geo/edition codes)
GOOGLE_NEWS_RSS = "https://news.google.com/rss"

# Map ISO-2 country codes → Google News edition codes
COUNTRY_TO_EDITION: dict[str, str] = {
    "US": "US:en", "GB": "GB:en", "CA": "CA:en", "AU": "AU:en",
    "IN": "IN:en", "DE": "DE:de", "FR": "FR:fr", "ES": "ES:es",
    "IT": "IT:it", "BR": "BR:pt-BR", "MX": "MX:es-419", "AR": "AR:es-419",
    "CL": "CL:es-419", "CO": "CO:es-419", "JP": "JP:ja", "KR": "KR:ko",
    "TR": "TR:tr", "PL": "PL:pl", "NL": "NL:nl", "SE": "SE:sv",
    "NO": "NO:no", "FI": "FI:fi", "RU": "RU:ru", "UA": "UA:uk",
    "ZA": "ZA:en", "NG": "NG:en", "EG": "EG:ar", "IL": "IL:he",
    "SA": "SA:ar", "AE": "AE:ar", "PK": "PK:en", "TH": "TH:th",
    "VN": "VN:vi", "ID": "ID:id", "MY": "MY:en", "SG": "SG:en",
    "PH": "PH:en", "NZ": "NZ:en", "PT": "PT:pt-PT", "BE": "BE:fr",
    "AT": "AT:de", "CH": "CH:de", "IE": "IE:en", "DK": "DK:da",
    "IS": "IS:is", "CZ": "CZ:cs", "HU": "HU:hu", "RO": "RO:ro",
    "BG": "BG:bg", "GR": "GR:el", "RS": "RS:sr", "HR": "HR:hr",
    "SI": "SI:sl", "SK": "SK:sk", "EE": "EE:et", "LV": "LV:lv",
    "LT": "LT:lt", "CN": "CN:zh-Hans", "TW": "TW:zh-Hant",
    "HK": "HK:zh-Hant", "PE": "PE:es-419", "VE": "VE:es-419",
    "EC": "EC:es-419", "KE": "KE:en", "MA": "MA:fr",
}

# Gemini API endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


class NewsService:
    """Fetch headlines via Google News RSS, analyze sentiment with Gemini."""

    def __init__(self):
        self._headline_cache: dict[str, list[str]] = {}
        self._summary_cache: dict[str, str] = {}

    async def fetch_sentiment(self, country_code: str) -> Optional[float]:
        """Return a sentiment score between -1.0 and 1.0 for a country's
        current headlines, or a fallback if unavailable."""
        cc = country_code.upper()

        # 1. Fetch headlines
        headlines = await self._fetch_headlines(cc)
        if not headlines:
            logger.warning("No headlines for %s, using fallback", cc)
            return self._fallback_sentiment(cc)

        # 2. Analyze with Gemini
        if settings.GEMINI_API_KEY:
            try:
                score = await self._gemini_analyze(cc, headlines)
                if score is not None:
                    return score
            except Exception as e:
                logger.warning("Gemini analysis failed for %s: %s", cc, e)

        # 3. Fallback to keyword-based if Gemini fails
        return self._keyword_score(headlines)

    async def fetch_headlines(self, country_code: str) -> list[str]:
        """Public method to get headlines for a country (used by API)."""
        return await self._fetch_headlines(country_code.upper())

    async def _fetch_headlines(self, cc: str, limit: int = 15) -> list[str]:
        """Fetch top headlines from Google News RSS for a country."""
        if cc in self._headline_cache:
            return self._headline_cache[cc]

        edition = COUNTRY_TO_EDITION.get(cc)
        if not edition:
            # Try generic English
            edition = f"{cc}:en"

        country_part, lang_part = edition.split(":", 1)
        url = f"{GOOGLE_NEWS_RSS}?hl={lang_part}&gl={country_part}&ceid={edition}"

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=10, follow_redirects=True)
                resp.raise_for_status()

                root = ElementTree.fromstring(resp.text)
                items = root.findall(".//item/title")
                headlines = []
                for item in items[:limit]:
                    text = item.text or ""
                    # Remove source suffix like " - BBC News"
                    text = re.sub(r"\s*-\s*[^-]+$", "", text).strip()
                    if text:
                        headlines.append(text)

                self._headline_cache[cc] = headlines
                logger.debug("Fetched %d headlines for %s", len(headlines), cc)
                return headlines

        except Exception as e:
            logger.warning("Google News RSS failed for %s: %s", cc, e)
            return []

    async def _gemini_analyze(self, cc: str, headlines: list[str]) -> Optional[float]:
        """Send headlines to Gemini and get a sentiment score."""
        headlines_text = "\n".join(f"- {h}" for h in headlines)

        prompt = f"""Analyze the following news headlines from {cc} and determine the overall emotional mood/sentiment of this country right now.

Headlines:
{headlines_text}

Based on these headlines, rate the overall national mood on a scale from -1.0 to 1.0 where:
- -1.0 = extremely negative (war, disasters, crises)
- -0.5 = negative (economic problems, social unrest)
- 0.0 = neutral
- 0.5 = positive (celebrations, achievements, growth)
- 1.0 = extremely positive (major victories, breakthroughs)

Respond with ONLY a JSON object in this exact format, nothing else:
{{"score": <float between -1.0 and 1.0>, "summary": "<one sentence summary of the mood in English>"}}"""

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 150,
            }
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GEMINI_API_URL}?key={settings.GEMINI_API_KEY}",
                json=payload,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            # Extract text from Gemini response
            text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )

            # Parse the JSON from Gemini's response
            import json
            # Try to extract JSON from the response
            json_match = re.search(r'\{[^}]+\}', text)
            if json_match:
                result = json.loads(json_match.group())
                score = float(result.get("score", 0))
                summary = result.get("summary", "")
                score = float(np.clip(score, -1.0, 1.0))
                # Cache the summary for later use
                self._summary_cache[cc] = summary
                logger.info("Gemini sentiment for %s: %.2f – %s", cc, score, summary)
                return round(score, 3)

        return None

    async def generate_mood_summary(
        self, 
        country_code: str, 
        country_name: str,
        mood_label: str,
        valence: float,
        energy: float,
        top_track: Optional[str] = None,
        top_genre: Optional[str] = None,
        headlines: Optional[list[str]] = None
    ) -> str:
        """Generate a one-sentence AI summary combining music and news mood."""
        cc = country_code.upper()
        
        # Return cached if available
        if cc in self._summary_cache and self._summary_cache[cc]:
            return self._summary_cache[cc]
        
        if not settings.GEMINI_API_KEY:
            return self._generate_fallback_summary(country_name, mood_label, valence, energy, top_genre)
        
        # Build context
        music_context = f"Music data: valence={valence:.2f} (happiness), energy={energy:.2f}"
        
        news_context = ""
        if headlines and len(headlines) > 0:
            news_context = "Today's news headlines:\n" + "\n".join(f"- {h}" for h in headlines[:5])
        
        prompt = f"""You are a cultural mood analyst for {country_name}. Based on the music listening patterns AND current news, write ONE insightful sentence (max 20 words) about what people in {country_name} are feeling right now.

{music_context}
Overall mood: {mood_label}

{news_context}

IMPORTANT: Your sentence MUST mention something specific from the news headlines if available. Connect the music mood with current events.
Example good responses:
- "Germans feel cautious optimism as economic news improves, reflected in upbeat pop choices."
- "Tensions from border news create anxious energy, yet Turks find solace in melancholic ballads."
- "Brazilians celebrate football victory with high-energy dance tracks dominating the charts."

Reply with ONLY your one sentence, nothing else."""

        try:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.8,
                    "maxOutputTokens": 60,
                }
            }
            
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{GEMINI_API_URL}?key={settings.GEMINI_API_KEY}",
                    json=payload,
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
                
                text = (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                ).strip()
                
                if text:
                    self._summary_cache[cc] = text
                    logger.info("Generated mood summary for %s: %s", cc, text)
                    return text
                    
        except Exception as e:
            logger.warning("Gemini summary failed for %s: %s", cc, e)
        
        return self._generate_fallback_summary(country_name, mood_label, valence, energy, top_genre, headlines)
    
    @staticmethod
    def _generate_fallback_summary(
        country_name: str, 
        mood_label: str, 
        valence: float, 
        energy: float, 
        top_genre: Optional[str],
        headlines: Optional[list[str]] = None
    ) -> str:
        """Generate a simple fallback summary without AI."""
        mood_desc = {
            "Happy": "experiencing optimistic vibes today",
            "Calm": "in a peaceful and steady state",
            "Sad": "reflecting on challenging times",
            "Angry": "feeling tense amid recent events",
            "Anxious": "navigating uncertain times"
        }
        desc = mood_desc.get(mood_label, "experiencing mixed feelings")
        
        # Try to add context from headlines
        if headlines and len(headlines) > 0:
            return f"{country_name} is {desc} as news unfolds across the nation."
        
        return f"{country_name} is {desc}."

    @staticmethod
    def _keyword_score(headlines: list[str]) -> float:
        """Fallback keyword-based sentiment when Gemini is unavailable."""
        POSITIVE = frozenset([
            "win", "celebrate", "peace", "growth", "success", "record",
            "breakthrough", "victory", "improve", "rise", "gain", "boost",
            "hope", "joy", "festival", "achievement", "award",
        ])
        NEGATIVE = frozenset([
            "war", "crisis", "attack", "death", "crash", "protest",
            "disaster", "flood", "kill", "bomb", "fire", "earthquake",
            "recession", "inflation", "poverty", "violence", "terror",
        ])

        scores = []
        for h in headlines:
            words = h.lower().split()
            pos = sum(1 for w in words if any(p in w for p in POSITIVE))
            neg = sum(1 for w in words if any(n in w for n in NEGATIVE))
            total = pos + neg
            if total == 0:
                scores.append(0.0)
            else:
                scores.append((pos - neg) / total)

        if not scores:
            return 0.0
        return round(float(np.clip(np.mean(scores), -1.0, 1.0)), 3)

    @staticmethod
    def _fallback_sentiment(country_code: str) -> float:
        """Deterministic synthetic sentiment for when no data is available."""
        import hashlib
        seed = int(hashlib.md5(f"news-{country_code}".encode()).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        return round(float(rng.uniform(-0.3, 0.5)), 3)
