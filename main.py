from src.models import *
from src.utils import *
from src.agent import get_langgraph_response

def qa_memory_live(user_id):
    history = []

    while True:
        audio_path = record_until_silence()
        query = stt(audio_path)
        print(f"🗣️ You: {query}")

        # Intent classifier
        intent = llm(
            system_prompt=get_prompt("intent_classifer"),
            query=query
        )
        if intent.strip().upper() == "EXIT":
            print("👋 Exiting conversation...")
            break

        # LLM Response with history
        response = get_langgraph_response(user_number=user_id, user_input=query)
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
    qa_memory_live(user_id = 2)