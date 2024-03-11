from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import subprocess
import torch
from TTS.api import TTS
from pydub import AudioSegment
import speech_recognition as sr
from translate import Translator
import noisereduce as nr
import moviepy.editor as mp
from werkzeug.utils import secure_filename

app = Flask(__name__)

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

device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file.save(filename)
        input_video_path = filename
        if not os.path.exists(input_video_path):
            return "File not found."
        else:
            subprocess.run(["ffmpeg", "-i", input_video_path, "-c:v", "copy", "only_video.mp4"])
            subprocess.run(["ffmpeg", "-i", input_video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "only_audio.wav"])
            cleaned_audio_file = remove_background_noise("only_audio.wav")
            print(f"Background noise removed. Cleaned audio saved as '{cleaned_audio_file}'")

            # Process the audio
            vocals_text = transcribe_and_translate_audio(cleaned_audio_file, target_language='hi')
            if vocals_text:  # Only perform TTS if there is text
                with open("vocal_text.txt", "w", encoding="utf-8") as output_file:
                    output_file.write(vocals_text)
                print("Exported vocals_text to vocal_text.txt")
                with open("vocal_text.txt", "r", encoding="utf-8") as file:
                    vocals_text = file.read()
                tts.tts_to_file(text=vocals_text, speaker_wav=cleaned_audio_file, language="hi", file_path="output.wav")

            # Combine the audio and video
            subprocess.run(["ffmpeg", "-i", "only_video.mp4", "-i", "output.wav", "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", "-map", "0:v:0", "-map", "1:a:0", "Final_output.mp4"])

            return send_file('Final_output.mp4', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
