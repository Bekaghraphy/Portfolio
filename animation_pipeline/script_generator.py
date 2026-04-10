"""
Step 1 — Script Generation using Claude API.

Generates a structured animation video script with:
  - Title
  - Hook (opening line)
  - Scenes (each with narration + visual description for image generation)
  - Call-to-action
"""

import json
import re
from dataclasses import dataclass
from typing import List

import anthropic

from config import config


@dataclass
class Scene:
    scene_number: int
    narration: str          # Text spoken in voice-over
    visual_prompt: str      # DALL-E prompt for background image
    duration_hint: float = 5.0  # seconds (overridden by TTS audio length)


@dataclass
class VideoScript:
    title: str
    hook: str
    scenes: List[Scene]
    call_to_action: str
    youtube_description: str
    tags: List[str]


SCRIPT_SYSTEM_PROMPT = """You are an expert animation video scriptwriter.
You create engaging, educational short-form animation scripts (60–120 seconds).
Each script must follow the exact JSON structure requested.
Keep narration natural, conversational, and suitable for Arabic or English TTS.
Visual prompts must be vivid, cinematic, and animation-friendly (no real people, no text in images)."""

SCRIPT_USER_TEMPLATE = """Create an animation video script about: "{topic}"

Target language: {language}
Target audience: {audience}
Video style: {style}

Return ONLY valid JSON in this exact structure:
{{
  "title": "catchy video title",
  "hook": "one powerful opening sentence (max 15 words)",
  "scenes": [
    {{
      "scene_number": 1,
      "narration": "what the narrator says (2-4 sentences)",
      "visual_prompt": "detailed DALL-E image prompt for this scene background — cinematic, {style} animation style, no text, no real people"
    }}
  ],
  "call_to_action": "final CTA sentence (subscribe / follow / etc.)",
  "youtube_description": "150-word SEO-optimised YouTube description",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}

Requirements:
- 4 to 6 scenes total
- Each narration: 2–4 sentences, natural spoken language
- Each visual_prompt: detailed, art-direction quality
- title: compelling, SEO-friendly
- tags: 5–10 relevant tags"""


def generate_script(
    topic: str,
    language: str = "Arabic",
    audience: str = "general public",
    style: str = "modern flat 2D animation",
) -> VideoScript:
    """Call Claude to generate a structured video script."""

    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    prompt = SCRIPT_USER_TEMPLATE.format(
        topic=topic,
        language=language,
        audience=audience,
        style=style,
    )

    print(f"[Script] Generating script for: '{topic}' ...")

    message = client.messages.create(
        model=config.claude_model,
        max_tokens=config.script_max_tokens,
        system=SCRIPT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Extract JSON block if wrapped in markdown code fences
    json_match = re.search(r"```(?:json)?\s*([\s\S]+?)```", raw)
    if json_match:
        raw = json_match.group(1).strip()

    data = json.loads(raw)

    scenes = [
        Scene(
            scene_number=s["scene_number"],
            narration=s["narration"],
            visual_prompt=s["visual_prompt"],
        )
        for s in data["scenes"]
    ]

    script = VideoScript(
        title=data["title"],
        hook=data["hook"],
        scenes=scenes,
        call_to_action=data["call_to_action"],
        youtube_description=data["youtube_description"],
        tags=data.get("tags", []),
    )

    print(f"[Script] Done — {len(scenes)} scenes generated.")
    return script


def save_script(script: VideoScript, path: str) -> None:
    """Save the script as a JSON file for review / re-use."""
    data = {
        "title": script.title,
        "hook": script.hook,
        "scenes": [
            {
                "scene_number": s.scene_number,
                "narration": s.narration,
                "visual_prompt": s.visual_prompt,
            }
            for s in script.scenes
        ],
        "call_to_action": script.call_to_action,
        "youtube_description": script.youtube_description,
        "tags": script.tags,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Script] Saved to {path}")


def load_script(path: str) -> VideoScript:
    """Load a previously saved script JSON."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    scenes = [
        Scene(
            scene_number=s["scene_number"],
            narration=s["narration"],
            visual_prompt=s["visual_prompt"],
        )
        for s in data["scenes"]
    ]
    return VideoScript(
        title=data["title"],
        hook=data["hook"],
        scenes=scenes,
        call_to_action=data["call_to_action"],
        youtube_description=data["youtube_description"],
        tags=data.get("tags", []),
    )
