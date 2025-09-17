from src.models import *
from src.utils import *
from src.historymng import *


def qa_memory_live():
    history = []

    while True:
        audio_path = record_until_silence()
        query = stt(audio_path)
        print(f"🗣️ You: {query}")
        save_message("user", query)

        # Intent classifier
        intent = llm(
            system_prompt=get_prompt("intent_classifer"),
            query=query
        )
        if intent.strip().upper() == "EXIT":
            print("👋 Exiting conversation...")
            save_message("system", "EXIT triggered, conversation ended")
            break

        # Build full context from history
        context_query = build_context(query, limit=10)

        # LLM Response with history
        response = llm(
            system_prompt=get_prompt("general"),
            query=context_query
        )
        print(f"🤖 Bot: {response}")
        save_message("bot", response)

        # TTS
        filename = tts(response)
        play_audio(filename)
        # Save to history
        history.append({"user": query, "bot": response})

    print("\n📜 Conversation History:")
    for turn in history:
        print(f"👤 {turn['user']} → 🤖 {turn['bot']}")


if __name__ == "__main__":
    qa_memory_live()