"""
Step 3b — Video Composition using MoviePy.

Combines:
  - Scene background images (Ken Burns zoom effect)
  - Voice-over audio per scene
  - Subtitle text overlay
  - Smooth crossfade transitions between scenes
  - Background music (optional)

Output: a single MP4 ready for YouTube upload.
"""

import os
from pathlib import Path
from typing import List, Optional

import numpy as np
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    concatenate_videoclips,
    afx,
)
from PIL import Image

from config import config
from script_generator import Scene
from voice_generator import get_audio_duration


# ---------- Ken Burns zoom effect ----------

def _zoom_image(image_path: str, duration: float, zoom_factor: float = 1.08) -> ImageClip:
    """
    Apply a slow Ken Burns zoom-in effect to a static image.
    zoom_factor: final scale (1.08 = 8% zoom over the clip duration)
    """
    img = np.array(Image.open(image_path).convert("RGB").resize(config.resolution))

    def make_frame(t: float):
        progress = t / duration
        scale = 1.0 + (zoom_factor - 1.0) * progress
        h, w = img.shape[:2]
        new_h = int(h / scale)
        new_w = int(w / scale)
        y0 = (h - new_h) // 2
        x0 = (w - new_w) // 2
        cropped = img[y0 : y0 + new_h, x0 : x0 + new_w]
        from PIL import Image as PILImage
        resized = np.array(
            PILImage.fromarray(cropped).resize((w, h), PILImage.LANCZOS)
        )
        return resized

    return ImageClip(make_frame, duration=duration, ismask=False)


# ---------- Subtitle overlay ----------

def _make_subtitle(
    text: str,
    duration: float,
    video_size: tuple,
    font_size: int = None,
    font_color: str = None,
) -> TextClip:
    """Create a subtitle TextClip with semi-transparent background."""
    font_size = font_size or config.font_size
    font_color = font_color or config.font_color

    txt_clip = (
        TextClip(
            text,
            fontsize=font_size,
            color=font_color,
            font="Arial-Bold",
            method="caption",
            size=(video_size[0] - 160, None),
            align="center",
        )
        .set_duration(duration)
        .set_position(("center", "bottom"))
        .margin(bottom=60, opacity=0)
    )

    # Semi-transparent dark background behind subtitle
    txt_w, txt_h = txt_clip.size
    bg = (
        ImageClip(
            np.zeros((txt_h + 20, txt_w + 40, 4), dtype=np.uint8),
            ismask=False,
        )
        .set_duration(duration)
        .set_opacity(config.subtitle_bg_opacity)
        .set_position(("center", "bottom"))
        .margin(bottom=55, opacity=0)
    )

    return CompositeVideoClip([bg, txt_clip], size=video_size).set_duration(duration)


# ---------- Main composer ----------

def compose_video(
    scenes: List[Scene],
    image_paths: List[str],
    audio_paths: List[str],
    output_path: str,
    hook_text: str = "",
    cta_text: str = "",
    bg_music_path: Optional[str] = None,
    bg_music_volume: float = 0.08,
    transition_duration: float = 0.5,
) -> str:
    """
    Compose the final video.

    Args:
        scenes: Scene list (for subtitle narration text)
        image_paths: paths to background images (same order as scenes)
        audio_paths: paths to MP3 files (hook + scenes + CTA order)
        output_path: where to write the final MP4
        hook_text: opening hook text
        cta_text: closing call-to-action text
        bg_music_path: optional background music file
        bg_music_volume: volume multiplier for background music
        transition_duration: crossfade length in seconds

    Returns:
        Path to the rendered MP4 file.
    """
    Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)

    # Build segments list: (text, image_path_or_None, audio_path)
    segments = []

    audio_iter = iter(audio_paths)

    if hook_text:
        segments.append((hook_text, None, next(audio_iter, None)))

    for i, scene in enumerate(scenes):
        img = image_paths[i] if i < len(image_paths) else None
        aud = next(audio_iter, None)
        segments.append((scene.narration, img, aud))

    if cta_text:
        segments.append((cta_text, None, next(audio_iter, None)))

    clips = []

    for idx, (text, img_path, aud_path) in enumerate(segments):
        # Determine duration from audio
        if aud_path and os.path.exists(aud_path):
            duration = get_audio_duration(aud_path) + 0.3  # tiny tail
        else:
            duration = config.scene_duration

        # Background
        if img_path and os.path.exists(img_path):
            bg = _zoom_image(img_path, duration)
        else:
            # Fallback: dark gradient for hook / CTA segments
            gradient = _dark_gradient(config.resolution, duration)
            bg = gradient

        # Audio
        if aud_path and os.path.exists(aud_path):
            audio = AudioFileClip(aud_path)
            bg = bg.set_audio(audio)

        # Subtitle overlay
        subtitle = _make_subtitle(text, duration, config.resolution)
        composite = CompositeVideoClip([bg, subtitle], size=config.resolution)
        composite = composite.set_duration(duration)

        # Crossfade in (except first clip)
        if idx > 0 and transition_duration > 0:
            composite = composite.crossfadein(transition_duration)

        clips.append(composite)

    print(f"[Video] Concatenating {len(clips)} clips ...")
    final = concatenate_videoclips(clips, method="compose", padding=-transition_duration)

    # Optional background music
    if bg_music_path and os.path.exists(bg_music_path):
        print(f"[Video] Adding background music: {bg_music_path}")
        music = AudioFileClip(bg_music_path).volumex(bg_music_volume)
        music = afx.audio_loop(music, duration=final.duration)
        music = music.set_duration(final.duration)
        if final.audio:
            from moviepy.editor import CompositeAudioClip
            final = final.set_audio(CompositeAudioClip([final.audio, music]))
        else:
            final = final.set_audio(music)

    print(f"[Video] Rendering to {output_path} ...")
    final.write_videofile(
        output_path,
        fps=config.fps,
        codec="libx264",
        audio_codec="aac",
        bitrate="8000k",
        threads=4,
        preset="slow",
        logger="bar",
    )

    print(f"[Video] Done: {output_path}")
    return output_path


def _dark_gradient(size: tuple, duration: float) -> ImageClip:
    """Create a dark animated gradient for hook/CTA slides."""
    w, h = size
    gradient = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        val = int(20 + 40 * (y / h))
        gradient[y, :] = [val // 3, val // 2, val]  # dark blue-ish

    return ImageClip(gradient, ismask=False).set_duration(duration)
