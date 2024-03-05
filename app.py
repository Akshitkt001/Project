from flask import Flask, render_template, request, redirect, url_for, flash
import os
import subprocess
import torch
import speech_recognition as sr
from translate import Translator
from TTS.api import TTS
from pydub import AudioSegment
import noisereduce as nr

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def remove_background_noise(audio_file):
    audio = AudioSegment.from_wav(audio_file)
    reduced_noise = nr.reduce_noise(audio.get_array_of_samples(), audio.frame_rate)
    cleaned_audio = AudioSegment(
        data=reduced_noise.tobytes(),
        sample_width=audio.sample_width,
        frame_rate=audio.frame_rate,
        channels=audio.channels
    )
    cleaned_audio.export("vocals.wav", format="wav")
    return "vocals.wav"

def transcribe_and_translate_audio(audio_path, target_language='en'):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data)
        translator = Translator(to_lang=target_language)
        translated_text = translator.translate(text)
        return translated_text
    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'video_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        video_file = request.files['video_file']
        if video_file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if video_file:
            video_file.save("input_video.mp4")
            input_video_path = "input_video.mp4"
            if not os.path.exists(input_video_path):
                flash("File not found.")
            else:
                subprocess.run(["ffmpeg", "-i", input_video_path, "-c:v", "copy", "only_video.mp4"])
                subprocess.run(["ffmpeg", "-i", input_video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "only_audio.wav"])
                cleaned_audio_file = remove_background_noise("only_audio.wav")
                flash(f"Background noise removed. Cleaned audio saved as '{cleaned_audio_file}'")
                flash("Processing completed.")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
