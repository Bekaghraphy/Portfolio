"""
Step 2 — Voice-over Generation using ElevenLabs TTS.

Converts each scene's narration text into an MP3 audio file.
Falls back to gTTS (Google Text-to-Speech) if ElevenLabs key is missing.
"""

import os
from pathlib import Path
from typing import List

from config import config
from script_generator import Scene


def _generate_elevenlabs(text: str, output_path: str) -> None:
    """Generate audio via ElevenLabs API (high quality, multilingual)."""
    import requests

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.elevenlabs_voice_id}"
    headers = {
        "xi-api-key": config.elevenlabs_api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": config.elevenlabs_model,
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.75,
            "style": 0.3,
            "use_speaker_boost": True,
        },
    }

    response = requests.post(url, json=payload, headers=headers, timeout=60)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)


def _generate_gtts(text: str, output_path: str, lang: str = "ar") -> None:
    """Fallback TTS using gTTS (free, lower quality)."""
    from gtts import gTTS

    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(output_path)


def generate_voiceovers(
    scenes: List[Scene],
    output_dir: str,
    hook: str = "",
    call_to_action: str = "",
    lang: str = "ar",
) -> List[str]:
    """
    Generate one MP3 per scene + hook + CTA.
    Returns a list of audio file paths in order.

    Args:
        scenes: list of Scene objects
        output_dir: directory to write MP3 files
        hook: opening hook text
        call_to_action: closing CTA text
        lang: language code for gTTS fallback ('ar' / 'en')
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    use_elevenlabs = bool(config.elevenlabs_api_key)
    method = "ElevenLabs" if use_elevenlabs else "gTTS (fallback)"
    print(f"[Voice] Using {method} TTS engine")

    audio_files: List[str] = []

    # Segments: hook → scenes → CTA
    segments = []
    if hook:
        segments.append(("hook", hook))
    for scene in scenes:
        segments.append((f"scene_{scene.scene_number:02d}", scene.narration))
    if call_to_action:
        segments.append(("cta", call_to_action))

    for name, text in segments:
        out_path = os.path.join(output_dir, f"audio_{name}.mp3")
        print(f"[Voice] Generating: {name} ...")

        try:
            if use_elevenlabs:
                _generate_elevenlabs(text, out_path)
            else:
                _generate_gtts(text, out_path, lang=lang)
            audio_files.append(out_path)
            print(f"[Voice] Saved: {out_path}")
        except Exception as exc:
            print(f"[Voice] WARNING — failed for '{name}': {exc}")
            if use_elevenlabs:
                print("[Voice] Retrying with gTTS fallback ...")
                _generate_gtts(text, out_path, lang=lang)
                audio_files.append(out_path)

    print(f"[Voice] Done — {len(audio_files)} audio files generated.")
    return audio_files


def get_audio_duration(audio_path: str) -> float:
    """Return duration of an MP3/WAV file in seconds."""
    from pydub import AudioSegment

    audio = AudioSegment.from_file(audio_path)
    return len(audio) / 1000.0
