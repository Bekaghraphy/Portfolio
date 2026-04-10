"""
Animation Video Automation Pipeline — Orchestrator
====================================================

Full pipeline:
  1. Generate script  (Claude API)
  2. Generate images  (DALL-E 3)
  3. Generate audio   (ElevenLabs / gTTS)
  4. Compose video    (MoviePy)
  5. Upload to YouTube

Usage:
  python main.py --topic "كيف يعمل الذكاء الاصطناعي" --lang ar
  python main.py --topic "How AI works" --lang en --privacy public
  python main.py --script existing_script.json --skip-script

  # Dry-run (no YouTube upload):
  python main.py --topic "Test" --lang en --no-upload

  # Custom style:
  python main.py --topic "climate change" --style "watercolor animation" --audience "students"
"""

import argparse
import os
import sys
from pathlib import Path

from config import config
from script_generator import generate_script, load_script, save_script
from voice_generator import generate_voiceovers
from image_generator import generate_scene_images
from video_composer import compose_video
from youtube_publisher import upload_to_youtube


def run_pipeline(
    topic: str = "",
    script_path: str = "",
    language: str = "Arabic",
    lang_code: str = "ar",
    audience: str = "general public",
    style: str = "modern flat 2D animation",
    privacy: str = "private",
    upload: bool = True,
    bg_music: str = "",
    job_name: str = "",
) -> dict:
    """
    Run the full automation pipeline.

    Returns a dict with paths and YouTube video ID (if uploaded).
    """
    # ── Job directory ──────────────────────────────────────────────────────────
    if not job_name:
        import re, time
        safe = re.sub(r"[^\w\s-]", "", topic or "video").strip()
        job_name = re.sub(r"\s+", "_", safe)[:40] + f"_{int(time.time())}"

    job_dir = os.path.join(config.output_dir, job_name)
    audio_dir = os.path.join(job_dir, "audio")
    image_dir = os.path.join(job_dir, "images")
    Path(job_dir).mkdir(parents=True, exist_ok=True)

    results = {"job_dir": job_dir}

    # ── Step 1: Script ─────────────────────────────────────────────────────────
    script_file = script_path or os.path.join(job_dir, "script.json")

    if script_path and os.path.exists(script_path):
        print(f"\n{'='*60}")
        print("STEP 1: Loading existing script ...")
        script = load_script(script_path)
    else:
        print(f"\n{'='*60}")
        print("STEP 1: Generating script with Claude ...")
        script = generate_script(
            topic=topic,
            language=language,
            audience=audience,
            style=style,
        )
        save_script(script, script_file)

    print(f"  Title  : {script.title}")
    print(f"  Scenes : {len(script.scenes)}")
    results["script_path"] = script_file

    # ── Step 2: Images ────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("STEP 2: Generating scene images with DALL-E 3 ...")
    image_paths = generate_scene_images(script.scenes, image_dir)
    results["image_paths"] = image_paths

    # ── Step 3: Voice-over ────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("STEP 3: Generating voice-over ...")
    audio_paths = generate_voiceovers(
        scenes=script.scenes,
        output_dir=audio_dir,
        hook=script.hook,
        call_to_action=script.call_to_action,
        lang=lang_code,
    )
    results["audio_paths"] = audio_paths

    # ── Step 4: Video ─────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("STEP 4: Composing final video ...")
    video_path = os.path.join(job_dir, f"{job_name}.mp4")
    compose_video(
        scenes=script.scenes,
        image_paths=image_paths,
        audio_paths=audio_paths,
        output_path=video_path,
        hook_text=script.hook,
        cta_text=script.call_to_action,
        bg_music_path=bg_music or None,
    )
    results["video_path"] = video_path

    # ── Step 5: YouTube ───────────────────────────────────────────────────────
    if upload:
        print(f"\n{'='*60}")
        print("STEP 5: Uploading to YouTube ...")
        video_id = upload_to_youtube(
            video_path=video_path,
            script=script,
            privacy_status=privacy,
        )
        results["youtube_video_id"] = video_id
        results["youtube_url"] = f"https://www.youtube.com/watch?v={video_id}"
        print(f"\n  YouTube URL: {results['youtube_url']}")
    else:
        print("\nSTEP 5: Skipping YouTube upload (--no-upload flag).")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE")
    print(f"  Job folder : {job_dir}")
    print(f"  Video      : {results.get('video_path')}")
    if "youtube_url" in results:
        print(f"  YouTube    : {results['youtube_url']}")

    return results


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Animation Video Automation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--topic", default="", help="Video topic (required unless --script given)")
    parser.add_argument("--script", default="", help="Path to existing script.json to skip generation")
    parser.add_argument("--lang", default="ar", help="TTS language code: ar / en (default: ar)")
    parser.add_argument("--language", default="Arabic", help="Language name for script: Arabic / English (default: Arabic)")
    parser.add_argument("--audience", default="general public", help="Target audience description")
    parser.add_argument("--style", default="modern flat 2D animation", help="Animation visual style")
    parser.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"],
                        help="YouTube privacy status (default: private)")
    parser.add_argument("--no-upload", action="store_true", help="Skip YouTube upload")
    parser.add_argument("--bg-music", default="", help="Path to background music file (optional)")
    parser.add_argument("--job-name", default="", help="Custom job name for output folder")

    args = parser.parse_args()

    if not args.topic and not args.script:
        parser.error("Provide either --topic or --script")

    run_pipeline(
        topic=args.topic,
        script_path=args.script,
        language=args.language,
        lang_code=args.lang,
        audience=args.audience,
        style=args.style,
        privacy=args.privacy,
        upload=not args.no_upload,
        bg_music=args.bg_music,
        job_name=args.job_name,
    )


if __name__ == "__main__":
    main()
