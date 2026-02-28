# Hindi Book Summary, Audio, and Video Generator

This project provides a CLI to:
- read text from `.txt` or `.pdf` books,
- create a Hindi summary,
- optionally generate Hindi MP3 audio from the summary,
- optionally generate a video from the audio using related images.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

## CLI usage

```bash
python src/hindi_audiobook_summary.py \
  --input <book.txt|book.pdf> \
  --summary-output output/summary.txt \
  [--audio-output output/summary_hi.mp3] \
  [--video-output output/summary_video.mp4 --images-dir images/] \
  [--ratio 0.3]
```

### Audio first (requested flow)

```bash
python src/hindi_audiobook_summary.py \
  --input The_Belief_Effect_Placebo.pdf \
  --summary-output output/the_belief_effect_summary.txt \
  --audio-output output/the_belief_effect_hindi.mp3
```

### Video later from summary audio

```bash
python src/hindi_audiobook_summary.py \
  --input The_Belief_Effect_Placebo.pdf \
  --summary-output output/the_belief_effect_summary.txt \
  --audio-output output/the_belief_effect_hindi.mp3 \
  --video-output output/the_belief_effect_video.mp4 \
  --images-dir images/
```

## Notes

- `gTTS` requires internet access at runtime to synthesize speech.
- Video generation requires `ffmpeg` and `ffprobe` installed on the system.
- `--video-output` requires both `--audio-output` and `--images-dir`.
