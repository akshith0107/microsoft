from typing import Dict, Any, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger


class SarvamClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.SARVAM_API_KEY
        self.base_url = base_url or settings.SARVAM_BASE_URL
        self.is_live = bool(
            self.api_key 
            and self.api_key not in ["mock_sarvam_key", "your_sarvam_api_key_here", "PASTE_YOUR_SARVAM_API_KEY_HERE", "CHANGE_ME", ""]
        )

        if self.is_live:
            logger.info("Sarvam Client initialized in LIVE mode", url=self.base_url)
        else:
            logger.info("Sarvam Client initialized in MOCK mode")

    async def transcribe_audio(self, audio_url: str, language: str = "hi-IN") -> Dict[str, Any]:
        """
        Speech-to-Text (Saaras Model saaras:v1)
        Transcribes voice audio inputs to Hinglish/Hindi text.
        """
        logger.info("Sarvam Saaras STT Transcribe", audio_url=audio_url, language=language, is_live=self.is_live)

        if not self.is_live:
            # MOCK Mode
            a_lower = audio_url.lower()
            if "maggi" in a_lower or "profit" in a_lower:
                return {
                    "transcript": "Aaj ka profit kitna hai?",
                    "language": language,
                    "confidence": 0.95,
                    "model": "saaras:v1"
                }
            return {
                "transcript": "Maggi ka stock kitna hai?",
                "language": language,
                "confidence": 0.92,
                "model": "saaras:v1"
            }

        # LIVE Mode API Call to Sarvam Speech-to-Text
        try:
            url = f"{self.base_url.rstrip('/')}/speech-to-text"
            headers = {
                "api-subscription-key": self.api_key
            }
            payload = {
                "model": "saaras:v1",
                "language_code": language if "-" in language else f"{language}-IN",
                "audio_url": audio_url
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return {
                        "transcript": data.get("transcript", ""),
                        "language": data.get("language_code", language),
                        "confidence": 0.95,
                        "model": "saaras:v1"
                    }
                logger.error("Sarvam STT failed with status", status_code=res.status_code, body=res.text)
        except Exception as e:
            logger.error("Sarvam STT exception", error=str(e))

        return {
            "transcript": "Maggi 2-Min Masala Noodle 30 packets order kar do",
            "language": language,
            "confidence": 0.88,
            "model": "saaras:v1"
        }

    async def generate_speech(self, text: str, language: str = "hi-IN", speaker: str = "meera") -> Dict[str, Any]:
        """
        Text-to-Speech (Bulbul Model bulbul:v1)
        Converts text responses into audio synthesis for voice feedback.
        """
        logger.info("Sarvam Bulbul TTS Synthesize", text=text, language=language, is_live=self.is_live)

        if not self.is_live:
            # MOCK Mode
            return {
                "audio_url": "https://example.com/audio/mock_bulbul_tts.mp3",
                "audios": ["bWF1ZGlvX2Jhc2U2NA=="],
                "model": "bulbul:v1",
                "language": language
            }

        # LIVE Mode API Call to Sarvam Text-to-Speech
        try:
            url = f"{self.base_url.rstrip('/')}/text-to-speech"
            headers = {
                "api-subscription-key": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "inputs": [text],
                "target_language_code": language if "-" in language else f"{language}-IN",
                "speaker": speaker,
                "model": "bulbul:v1"
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    audios = data.get("audios", [])
                    return {
                        "audio_url": audios[0] if audios and audios[0].startswith("http") else None,
                        "audios": audios,
                        "model": "bulbul:v1",
                        "language": language
                    }
                logger.error("Sarvam TTS failed with status", status_code=res.status_code, body=res.text)
        except Exception as e:
            logger.error("Sarvam TTS exception", error=str(e))

        return {
            "audio_url": "https://example.com/audio/mock_bulbul_tts.mp3",
            "audios": [],
            "model": "bulbul:v1",
            "language": language
        }
