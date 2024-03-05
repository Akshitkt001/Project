# backend.py

from flask import Flask, request, jsonify
from pydub import AudioSegment
import noisereduce as nr
import speech_recognition as sr
from translate import Translator

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
        return "Speech Recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

# Define the route for processing video
@app.route('/process_video', methods=['POST'])
def process_video():
    # Handle file upload
    if 'video' not in request.files:
        return jsonify({'error': 'No file part'})
    
    video_file = request.files['video']
    video_file.save('input_video.mp4')

    # Processing logic
    cleaned_audio_file = remove_background_noise("input_video.mp4")
    transcription = transcribe_and_translate_audio(cleaned_audio_file, target_language='hi')

    return jsonify({'message': 'Video processing complete.', 'transcription': transcription})

if __name__ == '__main__':
    app.run(debug=True)
