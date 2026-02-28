# Hindi Audio Book Summary + Video Generator

This repo now supports a full pipeline:

1. Read **Hindi text or PDF book**
2. Generate **chapter-wise Hindi summary**
3. Create **Hindi audiobook MP3**
4. Build **MP4 video** from that audio using **related images**

## Features

- PDF text extraction (`pypdf`)
- Hindi sentence splitting and extractive summarization
- Hindi audio generation (`gTTS`)
- Video generation from related images + audio (`ffmpeg`)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install optional runtime dependencies:

```bash
pip install gTTS pypdf
```

Also ensure these system tools are available for video mode:

- `ffmpeg`
- `ffprobe`

## Usage

### A) Text -> Summary

```bash
python src/hindi_audiobook_summary.py \
  --input-text examples/book.txt \
  --summary-output output/summary.txt
```

### B) PDF -> Summary + Hindi MP3

```bash
python src/hindi_audiobook_summary.py \
  --input-pdf examples/book.pdf \
  --summary-output output/summary.txt \
  --audio-output output/summary.mp3
```

### C) PDF -> Summary + MP3 + Video (with related images)

Put related images in a folder (e.g. `assets/images/`) and run:

```bash
python src/hindi_audiobook_summary.py \
  --input-pdf examples/book.pdf \
  --summary-output output/summary.txt \
  --audio-output output/summary.mp3 \
  --images-dir assets/images \
  --video-output output/summary_video.mp4
```

## Image guidance

- Use topic-relevant images from the same book theme/chapter.
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`.
- Images are shown as slideshow frames timed across full audio length.

## Notes

- Exactly one source input is required: `--input-text` OR `--input-pdf`.
- `--video-output` requires both `--audio-output` and `--images-dir`.
- Hindi punctuation (`।`) is supported in sentence splitting.
