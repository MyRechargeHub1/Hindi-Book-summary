# Hindi Audio Book Summary Generator

This repository now includes a lightweight Python pipeline to create **Hindi book summaries** and convert them into **audio narration**.

## What it does

- Reads a Hindi text file (book notes, chapter text, transcript, etc.)
- Generates a concise chapter-wise summary using extractive scoring
- Writes the summary to a `.txt` file
- Optionally converts the summary into Hindi MP3 audio using `gTTS`

## Project structure

- `src/hindi_audiobook_summary.py` – main CLI tool
- `tests/test_summarizer.py` – unit tests for summarization logic
- `requirements.txt` – Python dependencies

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For audio export, also install:

```bash
pip install gTTS
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
  --input examples/book.txt \
  --summary-output output/summary.txt \
  --audio-output output/summary.mp3
```

## Input format

- Plain UTF-8 text file.
- Chapters are optional. If present, use headings like:
  - `अध्याय 1: ...`
  - `Chapter 1: ...`

Without chapters, the full text is treated as one section.

## Notes

- Hindi sentence splitting works with `।`, `.`, `?`, and `!`.
- Audio generation uses Google Text-to-Speech (`gTTS`) and requires internet access.
