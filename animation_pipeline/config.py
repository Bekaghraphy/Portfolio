"""
Central configuration for the Animation Video Automation Pipeline.
All API keys and settings are loaded from environment variables.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class PipelineConfig:
    # ---------- Claude (Script Generation) ----------
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    claude_model: str = "claude-opus-4-6"
    script_max_tokens: int = 2000

    # ---------- ElevenLabs (Voice-over) ----------
    elevenlabs_api_key: str = field(default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", ""))
    elevenlabs_voice_id: str = field(
        default_factory=lambda: os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    )  # default: Rachel
    elevenlabs_model: str = "eleven_multilingual_v2"

    # ---------- OpenAI (Image Generation) ----------
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    dalle_model: str = "dall-e-3"
    image_size: str = "1792x1024"   # 16:9 widescreen
    image_quality: str = "hd"

    # ---------- YouTube ----------
    youtube_client_secrets_file: str = field(
        default_factory=lambda: os.getenv(
            "YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json"
        )
    )
    youtube_credentials_file: str = "youtube_token.json"

    # ---------- Video Settings ----------
    fps: int = 24
    resolution: tuple = (1920, 1080)
    # Duration per scene image (seconds) — overridden by TTS audio length
    scene_duration: float = 5.0
    # Font for subtitles overlay
    font_size: int = 48
    font_color: str = "white"
    subtitle_bg_opacity: float = 0.6

    # ---------- Paths ----------
    assets_dir: str = "assets"
    output_dir: str = "output"


# Singleton
config = PipelineConfig()
