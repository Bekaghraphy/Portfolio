# Animation Video Automation Pipeline

Fully automated system: **topic → script → voice → video → YouTube**

```
Topic
  │
  ▼
[1] Claude API  ──→  Structured Script (scenes + visual prompts)
                              │
          ┌───────────────────┴───────────────────┐
          ▼                                       ▼
[2] DALL-E 3                              [3] ElevenLabs TTS
    Scene images (1792×1024)                  Voice-over MP3s
          │                                       │
          └───────────────────┬───────────────────┘
                              ▼
                    [4] MoviePy Composer
                      Ken Burns zoom
                      Subtitle overlay
                      Crossfade transitions
                      Background music (opt.)
                              │
                              ▼
                        Final MP4
                              │
                              ▼
                  [5] YouTube Data API v3
                    Private / Unlisted / Public
```

---

## Setup

### 1. Install dependencies
```bash
cd animation_pipeline
pip install -r requirements.txt
```

Also install `ffmpeg` (required by MoviePy):
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### 2. Configure API keys
```bash
cp .env.example .env
# Edit .env and add your keys
```

### 3. YouTube OAuth setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable **YouTube Data API v3**
3. Create **OAuth 2.0 Client ID** (Desktop app type)
4. Download `client_secrets.json` → place it in `animation_pipeline/`
5. First run will open a browser for authorization; token is cached automatically

---

## Usage

```bash
# Arabic video (default)
python main.py --topic "كيف يعمل الذكاء الاصطناعي"

# English video, upload as unlisted
python main.py --topic "How AI works" --lang en --language English --privacy unlisted

# Custom style + audience
python main.py \
  --topic "climate change effects" \
  --lang en \
  --language English \
  --style "watercolor animation, warm colors" \
  --audience "high school students" \
  --privacy private

# Use existing script (skip generation step)
python main.py --script output/my_job/script.json

# No YouTube upload (local render only)
python main.py --topic "test" --no-upload

# Add background music
python main.py --topic "space exploration" --bg-music assets/music.mp3
```

---

## Output Structure

```
output/
└── كيف_يعمل_الذكاء_1713000000/
    ├── script.json          ← editable script
    ├── images/
    │   ├── scene_01.jpg
    │   ├── scene_02.jpg
    │   └── ...
    ├── audio/
    │   ├── audio_hook.mp3
    │   ├── audio_scene_01.mp3
    │   └── ...
    └── كيف_يعمل_الذكاء_1713000000.mp4   ← final video
```

---

## Pipeline Modules

| File | Responsibility |
|------|---------------|
| `config.py` | Central configuration + env loading |
| `script_generator.py` | Claude API → structured JSON script |
| `image_generator.py` | DALL-E 3 → scene background images |
| `voice_generator.py` | ElevenLabs / gTTS → MP3 per scene |
| `video_composer.py` | MoviePy → final MP4 with Ken Burns + subtitles |
| `youtube_publisher.py` | YouTube Data API v3 upload with retry |
| `main.py` | Orchestrator + CLI |

---

## API Keys Required

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| [Anthropic](https://console.anthropic.com/) | Script generation | $5 free credit |
| [OpenAI](https://platform.openai.com/) | DALL-E 3 images | $5 free credit |
| [ElevenLabs](https://elevenlabs.io/) | Voice-over | 10k chars/month free |
| [Google Cloud](https://console.cloud.google.com/) | YouTube upload | Free (quota limits) |

> **Tip:** ElevenLabs is optional — the pipeline falls back to Google TTS (gTTS) automatically if `ELEVENLABS_API_KEY` is not set.
