from src.hindi_audiobook_summary import split_sections, split_sentences, summarize_text


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
