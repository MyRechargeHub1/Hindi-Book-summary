from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

import requests
from gtts import gTTS
from pypdf import PdfReader

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def extract_text_from_pdf(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    text = "\n".join(page for page in pages if page).strip()
    if not text:
        raise ValueError(f"No extractable text found in PDF: {pdf_path}")
    return text


def split_text_for_tts(text: str, max_chars: int = 3500) -> list[str]:
    clean_text = re.sub(r"\s+", " ", text).strip()
    if len(clean_text) <= max_chars:
        return [clean_text]

    sentences = re.split(r"(?<=[।.!?])\s+", clean_text)
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(sentence) > max_chars:
            if current:
                chunks.append(" ".join(current).strip())
                current, current_len = [], 0
            for idx in range(0, len(sentence), max_chars):
                chunks.append(sentence[idx : idx + max_chars])
            continue

        projected = current_len + len(sentence) + (1 if current else 0)
        if projected > max_chars:
            chunks.append(" ".join(current).strip())
            current = [sentence]
            current_len = len(sentence)
        else:
            current.append(sentence)
            current_len = projected

    if current:
        chunks.append(" ".join(current).strip())

    return [chunk for chunk in chunks if chunk]


def ensure_ffmpeg(binary: str) -> None:
    if shutil.which(binary) is None:
        raise RuntimeError(f"{binary} is required but not installed.")


def build_hindi_audio_from_text(text: str, output_audio: Path, lang: str = "hi") -> None:
    chunks = split_text_for_tts(text)
    output_audio.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="tts_chunks_") as tmp:
        temp_dir = Path(tmp)
        chunk_paths: list[Path] = []

        for idx, chunk in enumerate(chunks, start=1):
            chunk_path = temp_dir / f"chunk_{idx:04d}.mp3"
            tts = gTTS(text=chunk, lang=lang)
            try:
                tts.save(str(chunk_path))
            except Exception as exc:
                raise RuntimeError(
                    "gTTS request failed while generating Hindi audio. Check internet/proxy access to Google TTS."
                ) from exc
            chunk_paths.append(chunk_path)

        if len(chunk_paths) == 1:
            output_audio.write_bytes(chunk_paths[0].read_bytes())
            return

        ensure_ffmpeg("ffmpeg")
        concat_list = temp_dir / "concat.txt"
        with concat_list.open("w", encoding="utf-8") as handle:
            for chunk_path in chunk_paths:
                handle.write(f"file '{chunk_path.resolve()}'\n")

        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_list),
            "-c",
            "copy",
            str(output_audio),
        ]
        subprocess.run(cmd, check=True)


def fetch_related_images(query: str, output_dir: Path, count: int = 8) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    search_resp = session.get(
        "https://commons.wikimedia.org/w/api.php",
        params={
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": "6",
            "gsrlimit": str(max(1, count * 2)),
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
        },
        timeout=30,
    )
    search_resp.raise_for_status()
    pages = search_resp.json().get("query", {}).get("pages", {})

    images: list[Path] = []
    for page in pages.values():
        if len(images) >= count:
            break
        image_info = (page.get("imageinfo") or [{}])[0]
        image_url = image_info.get("url")
        if not image_url:
            continue

        suffix = Path(image_url).suffix.lower()
        if suffix not in IMAGE_EXTENSIONS:
            continue

        image_name = page.get("title", "image").replace("File:", "").replace(" ", "_")
        image_path = output_dir / image_name
        img_resp = session.get(image_url, timeout=30)
        if img_resp.status_code != 200:
            continue
        image_path.write_bytes(img_resp.content)
        images.append(image_path)

    if not images:
        raise RuntimeError("Could not download related images from Wikimedia Commons.")
    return images


def get_audio_duration_seconds(audio_path: Path) -> float:
    ensure_ffmpeg("ffprobe")
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def create_video_from_audio_and_images(audio_path: Path, image_paths: Iterable[Path], output_video: Path) -> None:
    ensure_ffmpeg("ffmpeg")
    image_list = list(image_paths)
    if not image_list:
        raise ValueError("No images provided for video generation.")

    duration = get_audio_duration_seconds(audio_path)
    image_duration = max(3.0, duration / len(image_list))
    output_video.parent.mkdir(parents=True, exist_ok=True)

    concat_file = output_video.parent / f"{output_video.stem}_images.txt"
    with concat_file.open("w", encoding="utf-8") as handle:
        for image in image_list:
            handle.write(f"file '{image.resolve()}'\n")
            handle.write(f"duration {image_duration:.2f}\n")
        handle.write(f"file '{image_list[-1].resolve()}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-i",
        str(audio_path),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-vf",
        "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
        "-c:a",
        "aac",
        "-shortest",
        str(output_video),
    ]
    subprocess.run(cmd, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage-wise automation: create Hindi audio from PDF first, and video from audio later."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audio_cmd = subparsers.add_parser("audio", help="Create Hindi MP3 from a PDF")
    audio_cmd.add_argument("--pdf", type=Path, required=True, help="Input PDF path")
    audio_cmd.add_argument("--audio-output", type=Path, required=True, help="Output MP3 path")
    audio_cmd.add_argument("--lang", default="hi", help="TTS language code, default=hi")

    video_cmd = subparsers.add_parser("video", help="Create MP4 from existing audio and related images")
    video_cmd.add_argument("--audio", type=Path, required=True, help="Input MP3 path")
    video_cmd.add_argument("--video-output", type=Path, required=True, help="Output MP4 path")
    video_cmd.add_argument(
        "--images-dir",
        type=Path,
        help="Use images from this folder (jpg/png/webp). If omitted, images are auto-downloaded.",
    )
    video_cmd.add_argument(
        "--query",
        default="belief effect placebo psychology",
        help="Search query for automatic image download",
    )
    video_cmd.add_argument(
        "--auto-images-count",
        type=int,
        default=8,
        help="Number of images to auto-download when --images-dir is not provided",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "audio":
        text = extract_text_from_pdf(args.pdf)
        build_hindi_audio_from_text(text=text, output_audio=args.audio_output, lang=args.lang)
        return

    if args.images_dir:
        image_paths = [
            p
            for p in sorted(args.images_dir.iterdir())
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        ]
        if not image_paths:
            raise ValueError(f"No supported images found in {args.images_dir}")
    else:
        image_paths = fetch_related_images(query=args.query, output_dir=Path("output/auto_images"), count=args.auto_images_count)

    create_video_from_audio_and_images(args.audio, image_paths, args.video_output)


if __name__ == "__main__":
    main()
