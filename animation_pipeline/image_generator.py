"""
Step 3a — Scene Image Generation using DALL-E 3.

Generates one cinematic background image per scene using the visual_prompt
from the script.  Images are saved as JPEG for MoviePy compositing.
"""

import os
import urllib.request
from pathlib import Path
from typing import List

from openai import OpenAI

from config import config
from script_generator import Scene


def generate_scene_images(
    scenes: List[Scene],
    output_dir: str,
    style_suffix: str = "cinematic lighting, vibrant colors, 16:9 widescreen",
) -> List[str]:
    """
    Generate one HD image per scene via DALL-E 3.

    Args:
        scenes: list of Scene objects (each has visual_prompt)
        output_dir: where to save the JPEGs
        style_suffix: appended to every prompt for visual consistency

    Returns:
        List of image file paths in scene order.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    client = OpenAI(api_key=config.openai_api_key)

    image_paths: List[str] = []

    for scene in scenes:
        out_path = os.path.join(output_dir, f"scene_{scene.scene_number:02d}.jpg")
        prompt = f"{scene.visual_prompt}, {style_suffix}"

        print(f"[Image] Generating scene {scene.scene_number}: {prompt[:80]}...")

        try:
            response = client.images.generate(
                model=config.dalle_model,
                prompt=prompt,
                size=config.image_size,
                quality=config.image_quality,
                n=1,
            )

            image_url = response.data[0].url
            urllib.request.urlretrieve(image_url, out_path)
            image_paths.append(out_path)
            print(f"[Image] Saved: {out_path}")

        except Exception as exc:
            print(f"[Image] ERROR for scene {scene.scene_number}: {exc}")
            # Use a black placeholder so the pipeline can continue
            _create_placeholder(out_path, scene.scene_number)
            image_paths.append(out_path)

    print(f"[Image] Done — {len(image_paths)} images generated.")
    return image_paths


def _create_placeholder(path: str, scene_number: int) -> None:
    """Create a simple black fallback image when DALL-E fails."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (1920, 1080), color=(10, 10, 20))
    draw = ImageDraw.Draw(img)
    draw.text(
        (960, 540),
        f"Scene {scene_number}",
        fill=(200, 200, 200),
        anchor="mm",
    )
    img.save(path, "JPEG", quality=95)
