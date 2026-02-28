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

- Trigger on PDF push: generates summary + MP3.
- Manual trigger (`workflow_dispatch`): set `pdf_file`, then optionally set `make_video=true` with `images_dir`.
- Download outputs from Actions artifacts (`output/*.txt`, `output/*.mp3`, optional `output/*.mp4`).

## Notes

- PDF input requires `pypdf`.
- Audio generation uses `gTTS` (internet required).
- Video generation requires local images and `ffmpeg`/`ffprobe`.
