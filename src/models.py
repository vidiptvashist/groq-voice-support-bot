from load_variables import client


def llm(system_prompt, query):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"{system_prompt}"
            },
            {
                "role": "user",
                "content": f"{query}",
            }
        ],
        model="llama-3.1-8b-instant",
    )

    return chat_completion.choices[0].message.content

def stt(audio_path):
  # Specify the path to the audio file
  filename = f"{audio_path}"

  # Open the audio file
  with open(filename, "rb") as file:
      # Create a transcription of the audio file
      transcription = client.audio.transcriptions.create(
        file=file, # Required audio file
        model="whisper-large-v3-turbo", # Required model to use for transcription
        prompt="Specify context or spelling",  # Optional
        response_format="verbose_json",  # Optional
        timestamp_granularities = ["word", "segment"], # Optional (must set response_format to "json" to use and can specify "word", "segment" (default), or both)
        language="en",  # Optional
        temperature=0.0  # Optional
      )
      return transcription.text
  
def tts(text):
    speech_file_path = "audio/response.wav" 
    model = "playai-tts"
    voice = "Basil-PlayAI"
    response_format = "wav"

    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        response_format=response_format
    )
    response.write_to_file(speech_file_path)
    return speech_file_path

