import pdfplumber
from gtts import gTTS
import requests
import moviepy.editor as mp

def pdf_to_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

def text_to_audio(text, lang='hi'):
    tts = gTTS(text=text, lang=lang)
    audio_file = 'output.mp3'
    tts.save(audio_file)
    return audio_file

def download_images(image_urls):
    images = []
    for url in image_urls:
        response = requests.get(url)
        if response.status_code == 200:
            image_file = url.split("/")[-1]
            with open(image_file, 'wb') as f:
                f.write(response.content)
            images.append(image_file)
    return images

def create_video(audio_file, images):
    clips = [mp.ImageClip(img).set_duration(2) for img in images]
    video = mp.concatenate_videoclips(clips, method="compose")
    video.set_audio(mp.AudioFileClip(audio_file))
    video_file = 'output_video.mp4'
    video.write_videofile(video_file, fps=24)
    return video_file

# Example usage
pdf_path = 'example.pdf'
text = pdf_to_text(pdf_path)
audio_file = text_to_audio(text)
image_urls = ['http://example.com/image1.jpg', 'http://example.com/image2.jpg']
images = download_images(image_urls)
vide...