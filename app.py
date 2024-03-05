from flask import Flask, render_template, request, jsonify
from pydub import AudioSegment
import speech_recognition as sr
from translate import Translator
import noisereduce as nr
import moviepy.editor as mp
import subprocess
import os

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

def process_video(video_path):
    # Process video here (Example: just return the input video path)
    return video_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_video', methods=['POST'])
def process_video_route():
    video_file = request.files['video']
    video_file.save('input_video.mp4')

    input_video_path = 'input_video.mp4'
    if not os.path.exists(input_video_path):
        return jsonify({'error': 'File not found.'})

    # Simulating video processing (replace with actual processing logic)
    processed_video_path = process_video(input_video_path)

    return jsonify({'message': 'Video processing complete.', 'video_url': processed_video_path})

if __name__ == '__main__':
    app.run(debug=True)
