import sys
import time
import threading
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import wave
import speech_recognition as sr
from speech_recognition import AudioData

stop_event = threading.Event()
audio_frames = []

def wait_for_enter():
    input("\n Press Enter to stop recording...\n")
    stop_event.set()

def spinner():
    chars = '|/-\\'
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f'\r🔴 Recording... {chars[i % 4]}')
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)
    print("\r✅ Recording complete!      ")

def callback(indata, frames, time_info, status):
    if status:
        print(status)
    audio_frames.append(indata.copy())

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
    return audio_data.tobytes(), samplerate, 2  # 2 bytes for int16
def save_audio(data, rate, width, filename="recording.wav"):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(width)
        wf.setframerate(rate)
        wf.writeframes(data)
print(f"💾 Saved: {filename}")

def transcribe(data, rate, width):
    recognizer = sr.Recognizer()
    audio = AudioData(data, rate, width)
    try:
        text = recognizer.recognize_google(audio)
        print(f"📝 Transcription: {text}")
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
    except sr.RequestError as e:
        print(f"❌ API Error: {e}")

def plot_waveform(data, rate):
    samples = np.frombuffer(data, dtype=np.int16)
    time_axis = np.linspace(0, len(samples) / rate, len(samples))

    plt.figure(figsize=(10, 4))
    plt.plot(time_axis, samples)
    plt.title("Your Voice Waveform")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def main():
    print("=" * 40)
    print("🎙️ HELLO AI, CAN YOU HEAR ME?")
    print("=" * 40)

    print("\nSpeak into your microphone...")
    audio_data, rate, width = record_audio()

    save_audio(audio_data, rate, width)
    transcribe(audio_data, rate, width)
    plot_waveform(audio_data, rate)

if __name__ == "__main__":
    main()