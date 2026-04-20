# A class is a blueprint, an object is the actual thing built from it
# Think of a class like a cookie cutter, objects are the cookies

class AIAssistant:
    
    # runs when you create the object like a constructor 
    def __init__(self, name, model):
        self.name = name
        self.model = model
        self.conversation_history = []  # stores messages
    
    # method to ask a question
    def ask(self, question):
        self.conversation_history.append(question)
        return f"{self.name} answered: {question}"
    
    # method to show history
    def show_history(self):
        print(f"\n--- {self.name} conversation history ---")
        for i, msg in enumerate(self.conversation_history):
            print(f"{i + 1}. {msg}")
    
    # method to clear history
    def clear_history(self):
        self.conversation_history = []
        print("History cleared!")


# create two different assistants
assistant1 = AIAssistant("Claude", "claude-haiku-4-5-20251001")
assistant2 = AIAssistant("Helper", "claude-sonnet-4-20250514")

# use them
print(assistant1.ask("What is Python?"))
print(assistant1.ask("What is AI?"))
print(assistant2.ask("What is React?"))

# show history
assistant1.show_history()
assistant2.show_history()

# access properties
print(f"\nAssistant name: {assistant1.name}")
print(f"Model: {assistant1.model}")

# clear history
assistant1.clear_history()
assistant1.show_history()