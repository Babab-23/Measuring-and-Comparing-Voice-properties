import sys
import time
import threading
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import wave
import speech_recognition as sr

# Global variables
stop_event = threading.Event()
audio_frames = []

# Wait for Enter key to stop recording
def wait_for_enter():
    input("\nPress Enter to stop recording...\n")
    stop_event.set()

# Spinner animation
def spinner():
    chars = '|/-\\'
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f'\r🔴 Recording... {chars[i % 4]}')
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)
    print("\r✅ Recording complete!      ")

# Audio callback
def callback(indata, frames, time_info, status):
    if status:
        print(status)
    audio_frames.append(indata.copy())

# Record audio
def record_audio():
    global audio_frames
    audio_frames = []
    samplerate = 16000

    threading.Thread(target=wait_for_enter, daemon=True).start()
    threading.Thread(target=spinner, daemon=True).start()

    with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', callback=callback):
        while not stop_event.is_set():
            time.sleep(0.1)

    audio_data = np.concatenate(audio_frames, axis=0)
    return audio_data.tobytes(), samplerate

# Save audio to file
def save_audio(data, rate, filename="speech.wav"):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # int16 = 2 bytes
        wf.setframerate(rate)
        wf.writeframes(data)

# Transcribe audio
def transcribe_audio(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        print("\n📝 Transcription:", text)
    except:
        print("\n❌ Could not transcribe audio")

# Plot waveform
def plot_waveform(data):
    signal = np.frombuffer(data, dtype=np.int16)
    plt.title("Audio Waveform")
    plt.plot(signal)
    plt.xlabel("Samples")
    plt.ylabel("Amplitude")
    plt.show()

# MAIN PROGRAM
if __name__ == "__main__":
    print("🎤 Recording started...")
    
    audio_data, rate = record_audio()
    
    save_audio(audio_data, rate)
    print("💾 Audio saved as speech.wav")
    
    transcribe_audio("speech.wav")
    
    plot_waveform(audio_data)