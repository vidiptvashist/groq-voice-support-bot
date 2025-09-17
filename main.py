from src.models import *
from src.utils import *

def qa_live():
    history = []

    while True:
        # Record + STT
        audio_path = record_until_silence()
        query = stt(audio_path)
        print(f"🗣️ You: {query}")

        response = llm(
            system_prompt=get_prompt("intent_classifer"),
            query=query
        )
        if response.strip().upper() == "EXIT":
            print("👋 Exiting conversation...")
            break

        # LLM Response
        response = llm(system_prompt = get_prompt("general")
                       ,query = query)
        print(f"🤖 Bot: {response}")

        # TTS
        filename = tts(response)

        play_audio(filename)

        # Save to history
        history.append({"user": query, "bot": response})

    print("\n📜 Conversation History:")
    for turn in history:
        print(f"👤 {turn['user']} → 🤖 {turn['bot']}")


if __name__ == "__main__":
    qa_live()