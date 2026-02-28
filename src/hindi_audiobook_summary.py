from __future__ import annotations

import argparse
import re
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


@dataclass
class Section:
    title: str
    content: str


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Hindi book summary and optional audiobook audio.")
    parser.add_argument("--input", required=True, type=Path, help="Input UTF-8 text file")
    parser.add_argument("--summary-output", required=True, type=Path, help="Output summary text file")
    parser.add_argument("--audio-output", type=Path, help="Optional output mp3 path")
    parser.add_argument("--ratio", type=float, default=0.3, help="Summary ratio (0.1 to 0.9)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not (0.1 <= args.ratio <= 0.9):
        raise ValueError("--ratio must be between 0.1 and 0.9")

    source_text = args.input.read_text(encoding="utf-8")
    sections = split_sections(source_text)
    summary = summarize_sections(sections, ratio=args.ratio)

    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(summary, encoding="utf-8")

    if args.audio_output:
        create_audio(summary, args.audio_output)


if __name__ == "__main__":
    main()
