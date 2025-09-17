
import wavio
import numpy as np
import pygame
import sounddevice as sd


def play_ding(frequency=880, duration=0.2, samplerate=44100):
    pygame.mixer.init(frequency=samplerate, size=-16, channels=1)
    t = np.linspace(0, duration, int(samplerate * duration), False)
    tone = np.sin(frequency * t * 2 * np.pi)
    audio = (tone * 32767).astype(np.int16).tobytes()
    sound = pygame.mixer.Sound(buffer=audio)
    sound.play()
    pygame.time.delay(int(duration * 1000))


def record_until_silence(threshold=500, silence_duration=1.5, samplerate=16000, filename="audio/temp_input.wav"):
    print("🎤 Speak now...")
    play_ding()  # start ding
    audio = []
    silence_counter = 0

    with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16') as stream:
        while True:
            frame, _ = stream.read(1024)
            audio.append(frame)
            volume = np.abs(frame).mean()

            if volume < threshold:
                silence_counter += 1024 / samplerate
            else:
                silence_counter = 0

            if silence_counter > silence_duration:
                break

    audio_np = np.concatenate(audio, axis=0)
    wavio.write(filename, audio_np, samplerate, sampwidth=2)
    play_ding(frequency=440)  # end ding
    print("✅ Recording stopped (silence detected)")
    return filename


def play_audio(filename):
    try: 
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    finally:
        pygame.mixer.quit()  # ✅ clean up resources


import json

# Load prompts.json
with open("src/prompts.json", "r") as f:
    prompts = json.load(f)

def get_prompt(name):
    """Fetch a prompt by name and format with given variables."""
    prompt = prompts.get(name)
    system_prompt = prompt["system"]
    return system_prompt