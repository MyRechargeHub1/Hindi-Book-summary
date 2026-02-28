from __future__ import annotations

import argparse
import re
import shlex
import shutil
import subprocess
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

STOPWORDS = {
    "और",
    "है",
    "हैं",
    "था",
    "थी",
    "थे",
    "को",
    "के",
    "का",
    "की",
    "में",
    "से",
    "पर",
    "यह",
    "वह",
    "तो",
    "भी",
    "एक",
    "कि",
    "या",
    "लिए",
    "तक",
}

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass
class Section:
    title: str
    content: str


def extract_text_from_pdf(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("PDF input requires pypdf. Install with: pip install pypdf") from exc

    reader = PdfReader(str(pdf_path))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    text = "\n\n".join([p for p in pages if p])
    if not text.strip():
        raise ValueError(f"No extractable text found in PDF: {pdf_path}")
    return text


def load_source_text(input_text: Path | None, input_pdf: Path | None) -> str:
    if bool(input_text) == bool(input_pdf):
        raise ValueError("Provide exactly one source: --input-text or --input-pdf")

    if input_text:
        return input_text.read_text(encoding="utf-8")
    return extract_text_from_pdf(input_pdf)


def split_sections(text: str) -> list[Section]:
    pattern = re.compile(r"^(अध्याय\s*\d+.*|Chapter\s*\d+.*)$", flags=re.MULTILINE | re.IGNORECASE)
    matches = list(pattern.finditer(text))

    if not matches:
        return [Section(title="संपूर्ण पुस्तक", content=text.strip())]

    sections: list[Section] = []
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        title = match.group(1).strip()
        body = text[start:end].strip()
        if body:
            sections.append(Section(title=title, content=body))

    return sections or [Section(title="संपूर्ण पुस्तक", content=text.strip())]


def split_sentences(text: str) -> list[str]:
    chunks = re.split(r"(?<=[।.!?])\s+", text.strip())
    return [c.strip() for c in chunks if c.strip()]


def tokenize(sentence: str) -> list[str]:
    tokens = re.findall(r"[\u0900-\u097Fa-zA-Z]+", sentence.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def score_sentences(sentences: Iterable[str]) -> list[tuple[str, float]]:
    sentence_list = list(sentences)
    words: list[str] = []
    for sentence in sentence_list:
        words.extend(tokenize(sentence))

    if not sentence_list:
        return []

    freqs = Counter(words)
    if not freqs:
        return [(s, 0.0) for s in sentence_list]

    max_freq = max(freqs.values())
    weighted = {word: value / max_freq for word, value in freqs.items()}

    scores: list[tuple[str, float]] = []
    for sentence in sentence_list:
        token_list = tokenize(sentence)
        if not token_list:
            scores.append((sentence, 0.0))
            continue
        score = sum(weighted[t] for t in token_list) / len(token_list)
        scores.append((sentence, score))

    return scores


def summarize_text(text: str, ratio: float = 0.3, min_sentences: int = 2) -> str:
    sentences = split_sentences(text)
    if len(sentences) <= min_sentences:
        return " ".join(sentences)

    scored = score_sentences(sentences)
    keep_count = max(min_sentences, int(len(sentences) * ratio))

    top_sentences = set(s for s, _ in sorted(scored, key=lambda x: x[1], reverse=True)[:keep_count])
    ordered_summary = [s for s in sentences if s in top_sentences]
    return " ".join(ordered_summary)


def summarize_sections(sections: list[Section], ratio: float) -> str:
    output_lines: list[str] = []
    for section in sections:
        summary = summarize_text(section.content, ratio=ratio)
        output_lines.append(f"{section.title}\n{summary}\n")
    return "\n".join(output_lines).strip()


def create_audio(summary_text: str, output_path: Path) -> None:
    try:
        from gtts import gTTS
    except ImportError as exc:
        raise RuntimeError(
            "gTTS is required for audio output. Install it with: pip install gTTS"
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tts = gTTS(text=summary_text, lang="hi")
    tts.save(str(output_path))


def collect_related_images(images_dir: Path) -> list[Path]:
    if not images_dir.exists() or not images_dir.is_dir():
        raise ValueError(f"Images directory not found: {images_dir}")

    images = sorted([p for p in images_dir.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES])
    if not images:
        raise ValueError(f"No related images found in directory: {images_dir}")
    return images


def _audio_duration_seconds(audio_path: Path) -> float:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("ffprobe is required for video generation.")

    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]
    output = subprocess.check_output(cmd, text=True).strip()
    return max(1.0, float(output))


def create_video_from_audio(audio_path: Path, images: list[Path], output_path: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for video generation.")

    duration = _audio_duration_seconds(audio_path)
    per_image = max(1.0, duration / len(images))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        concat_file = Path(tmpdir) / "images.txt"
        lines: list[str] = []
        for image in images:
            lines.append(f"file {shlex.quote(str(image.resolve()))}")
            lines.append(f"duration {per_image:.2f}")
        lines.append(f"file {shlex.quote(str(images[-1].resolve()))}")
        concat_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        cmd = [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-i",
            str(audio_path),
            "-shortest",
            "-vf",
            "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            str(output_path),
        ]
        subprocess.run(cmd, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Hindi book summary, optional MP3 audio, and optional image-based video from PDF or text input."
    )
    parser.add_argument("--input-text", type=Path, help="Input UTF-8 text file")
    parser.add_argument("--input-pdf", type=Path, help="Input PDF book file")
    parser.add_argument("--summary-output", required=True, type=Path, help="Output summary text file")
    parser.add_argument("--audio-output", type=Path, help="Optional output mp3 path")
    parser.add_argument("--video-output", type=Path, help="Optional output mp4 path")
    parser.add_argument("--images-dir", type=Path, help="Folder containing related images for video")
    parser.add_argument("--ratio", type=float, default=0.3, help="Summary ratio (0.1 to 0.9)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not (0.1 <= args.ratio <= 0.9):
        raise ValueError("--ratio must be between 0.1 and 0.9")

    source_text = load_source_text(args.input_text, args.input_pdf)
    sections = split_sections(source_text)
    summary = summarize_sections(sections, ratio=args.ratio)

    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(summary, encoding="utf-8")

    if args.audio_output:
        create_audio(summary, args.audio_output)

    if args.video_output:
        if not args.audio_output:
            raise ValueError("--video-output requires --audio-output")
        if not args.images_dir:
            raise ValueError("--video-output requires --images-dir with related images")

        images = collect_related_images(args.images_dir)
        create_video_from_audio(args.audio_output, images, args.video_output)


if __name__ == "__main__":
    main()
