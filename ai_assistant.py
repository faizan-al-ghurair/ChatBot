import anthropic
import json
import os

class AIAssistant:

    def __init__(self, name, personality):
        self.name = name
        self.personality = personality
        self.client = anthropic.Anthropic()
        self.history_file = f"{self.name}_history.json"
        self.conversation_history = self.load_history()  # load on startup

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                print("Previous history loaded!")
                return json.load(f)
        return []  # fresh start if no file exists

    def save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.conversation_history, f, indent=2)
        print(f"History saved!")

    def ask(self, question):
        self.conversation_history.append({
            "role": "user",
            "content": question
        })

        try:
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=256,
                system=self.personality,
                messages=self.conversation_history
            )

            answer = response.content[0].text

            self.conversation_history.append({
                "role": "assistant",
                "content": answer
            })

            self.save_history()  # auto save after every message
            return answer

        except Exception as e:
            return f"Error: {e}"

    def show_history(self):
        print(f"\n--- {self.name} conversation history ---")
        for msg in self.conversation_history:
            role = "You" if msg["role"] == "user" else self.name
            print(f"{role}: {msg['content']}")

    def clear_history(self):
        self.conversation_history = []
        self.save_history()
        print("History cleared!")


# create your assistant
assistant = AIAssistant(
    name="PyHelper",
    personality="You are a helpful Python and AI coding assistant. Keep answers short and beginner friendly."
)

print(f"Chat with {assistant.name} — type 'history', 'clear', or 'quit'")
print("-" * 40)

while True:
    user_input = input("\nYou: ").strip()

    if user_input == "":
        continue
    elif user_input.lower() == "quit":
        print("Goodbye!")
        break
    elif user_input.lower() == "history":
        assistant.show_history()
    elif user_input.lower() == "clear":
        assistant.clear_history()
    else:
        response = assistant.ask(user_input)
        print(f"\n{assistant.name}: {response}")