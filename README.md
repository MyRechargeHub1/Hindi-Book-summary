# Hindi Audio Book Summary Generator

This repository includes a Python pipeline to create **Hindi book summaries** from text or PDF files, convert them into **audio narration**, and optionally generate a **video with related images**.

## What it does

- Reads a Hindi `.txt` or `.pdf` book file
- Generates a concise chapter-wise summary using extractive scoring
- Writes the summary to a `.txt` file
- Optionally converts the summary into Hindi MP3 audio using `gTTS`
- Optionally creates an MP4 video from audio + related images using `ffmpeg`

## Project structure

- `src/hindi_audiobook_summary.py` – main CLI tool
- `tests/test_summarizer.py` – unit tests for summarization and image selection logic
- `requirements.txt` – Python dependencies

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For video generation, install ffmpeg on your system:

```bash
sudo apt-get install ffmpeg
```

## Usage

### 1) Create summary text only

```bash
python src/hindi_audiobook_summary.py \
  --input examples/book.txt \
  --summary-output output/summary.txt
```

### 2) Create summary + Hindi audiobook (MP3)

```bash
python src/hindi_audiobook_summary.py \
  --input The_Power_of_Discipline_by_Muneer_Shah.pdf \
  --summary-output output/summary.txt \
  --audio-output output/summary.mp3
```

### 3) Create summary + audio + video from related images

```bash
python src/hindi_audiobook_summary.py \
  --input The_Power_of_Discipline_by_Muneer_Shah.pdf \
  --summary-output output/summary.txt \
  --audio-output output/summary.mp3 \
  --images-dir assets/discipline_images \
  --video-output output/summary_video.mp4
```


## GitHub Actions automation

This repo includes a workflow at `.github/workflows/pdf_to_hindi_audio_video.yml` that can run in the cloud:

- On every PDF push (`**/*.pdf`): generates summary + Hindi MP3.
- Via manual run (`workflow_dispatch`): can generate summary + MP3, and optionally MP4 (when `make_video=true` and `images_dir` is provided).

### Run from GitHub UI

1. Go to **Actions** → **PDF to Hindi Audio (and optional Video)**.
2. Click **Run workflow**.
3. Set:
   - `pdf_file` (for example `The_Belief_Effect_Placebo.pdf`)
   - `make_video` = `false` (audio first), or `true`
   - `images_dir` only when video is required (for example `assets/related_images`)
4. Download generated files from workflow artifacts (`output/*.txt`, `output/*.mp3`, optional `output/*.mp4`).

## Input format

- UTF-8 text (`.txt`) or PDF (`.pdf`) file.
- Chapters are optional. If present, use headings like:
  - `अध्याय 1: ...`
  - `Chapter 1: ...`

Without chapters, the full text is treated as one section.

## Notes

- Hindi sentence splitting works with `।`, `.`, `?`, and `!`.
- Audio generation uses Google Text-to-Speech (`gTTS`) and requires internet access.
- Video generation requires local images in `--images-dir` and `ffmpeg`/`ffprobe` binaries.
