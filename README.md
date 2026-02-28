# Hindi PDF → Hindi Audio → Video (Stage-wise)

This repository now supports the exact requested flow for `The_Belief_Effect_Placebo.pdf`:

1. **First** generate Hindi audio from PDF text.
2. **Later** generate video from that audio using related images.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> `ffmpeg` and `ffprobe` are required for MP3 chunk merge and video rendering.

## 1) First make Hindi audio from the PDF

```bash
python automated_audiobook_to_video.py audio \
  --pdf The_Belief_Effect_Placebo.pdf \
  --audio-output output/The_Belief_Effect_Placebo_hi.mp3
```

## 2) Later make video from the existing audio

### Option A: Auto-download related images (Wikimedia Commons)

```bash
python automated_audiobook_to_video.py video \
  --audio output/The_Belief_Effect_Placebo_hi.mp3 \
  --video-output output/The_Belief_Effect_Placebo_video.mp4 \
  --query "belief placebo psychology"
```

### Option B: Use your own image folder

```bash
python automated_audiobook_to_video.py video \
  --audio output/The_Belief_Effect_Placebo_hi.mp3 \
  --video-output output/The_Belief_Effect_Placebo_video.mp4 \
  --images-dir images/
```

## Notes

- Large PDFs are split into TTS-safe chunks automatically.
- Hindi TTS is generated with `gTTS` (`lang=hi`).
- If `--images-dir` is not provided, related images are downloaded automatically.
