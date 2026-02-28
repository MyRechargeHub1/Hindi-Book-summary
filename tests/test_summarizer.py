from pathlib import Path

from src.hindi_audiobook_summary import (
    pick_related_images,
    split_sections,
    split_sentences,
    summarize_text,
)


def test_split_sections_with_chapters() -> None:
    text = """अध्याय 1: शुरुआत
यह पहली कहानी है। इसमें एक पात्र है।
अध्याय 2: मोड़
यह दूसरी कहानी है। इसमें सीख है।"""
    sections = split_sections(text)

    assert len(sections) == 2
    assert sections[0].title.startswith("अध्याय 1")
    assert "पहली कहानी" in sections[0].content


def test_split_sentences_hindi_punctuation() -> None:
    text = "यह पहला वाक्य है। यह दूसरा वाक्य है! क्या यह तीसरा वाक्य है? हाँ।"
    sentences = split_sentences(text)

    assert len(sentences) == 4


def test_summarize_text_returns_content() -> None:
    text = """यह पुस्तक अनुशासन के बारे में है। अनुशासन से लक्ष्य प्राप्त होते हैं।
    लक्ष्य पाने के लिए नियमित अभ्यास जरूरी है। अभ्यास से आत्मविश्वास बढ़ता है।
    आत्मविश्वास से व्यक्ति बेहतर निर्णय लेता है।"""

    summary = summarize_text(text, ratio=0.4, min_sentences=2)

    assert "अनुशासन" in summary or "अभ्यास" in summary
    assert len(summary) > 20


def test_pick_related_images_scores_filenames(tmp_path: Path) -> None:
    (tmp_path / "mindset_growth.jpg").write_bytes(b"x")
    (tmp_path / "health_sleep.png").write_bytes(b"x")
    (tmp_path / "neutral.webp").write_bytes(b"x")

    summary = "यह अध्याय growth mindset और positive health आदतों पर आधारित है।"
    ranked = pick_related_images(summary, tmp_path)

    assert ranked[0].name in {"mindset_growth.jpg", "health_sleep.png"}
    assert len(ranked) == 3
