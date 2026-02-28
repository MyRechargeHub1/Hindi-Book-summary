# Hindi Audio Book Summary Generator

This project turns Hindi/English book content into:

- summary text
- Hindi MP3 narration
- optional MP4 video (audio + related images)

It supports both `.txt` and `.pdf` input files.

## Project structure

- `src/hindi_audiobook_summary.py` – CLI for summary/audio/video generation
- `tests/test_summarizer.py` – unit tests for text processing and image ranking
- `.github/workflows/pdf_to_hindi_audio_video.yml` – optional cloud automation via GitHub Actions
- `requirements.txt` – Python dependencies

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For video generation, install ffmpeg/ffprobe:

```bash
sudo apt-get install ffmpeg
```

## CLI usage

### 1) Summary only

```bash
python src/hindi_audiobook_summary.py \
  --input examples/book.txt \
  --summary-output output/summary.txt
```

### 2) PDF -> summary + Hindi MP3 (audio first)

```bash
python src/hindi_audiobook_summary.py \
  --input The_Belief_Effect_Placebo.pdf \
  --summary-output output/the_belief_effect_summary.txt \
  --audio-output output/the_belief_effect_hindi.mp3
```

### 3) PDF -> summary + MP3 + MP4 (related images)

```bash
python src/hindi_audiobook_summary.py \
  --input The_Belief_Effect_Placebo.pdf \
  --summary-output output/the_belief_effect_summary.txt \
  --audio-output output/the_belief_effect_hindi.mp3 \
  --images-dir assets/related_images \
  --video-output output/the_belief_effect_video.mp4
```

## GitHub Actions automation

Workflow file: `.github/workflows/pdf_to_hindi_audio_video.yml`

### Trigger-ready run (audio first)

1. Go to **Actions** -> **PDF to Hindi Audio (and optional Video)**.
2. Click **Run workflow**.
3. Keep: `make_video = false`.
4. Set: `pdf_file = The_Belief_Effect_Placebo.pdf` (or another repo PDF path).
5. Click **Run workflow** and download artifact files (`output/*_summary.txt`, `output/*_hindi.mp3`).

### Move to video step later

- Re-run with `make_video = true` and provide `images_dir` that contains at least one `.jpg/.jpeg/.png/.webp` file.
- The workflow validates `images_dir` existence and image presence before running video generation.

### Workflow behavior

- Trigger on PDF push: generates summary + MP3 only.
- Manual trigger (`workflow_dispatch`): generates summary + MP3, and optional MP4 when requested.
- Outputs are uploaded as a single artifact from `output/*`.

## Notes

- PDF input requires `pypdf`.
- Audio generation uses `gTTS` (internet required).
- Video generation requires local images and `ffmpeg`/`ffprobe`.
