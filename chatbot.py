from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    question: str

client = anthropic.Anthropic()

# ─── load policy files on startup ───────────────────────────────────────────

def load_policies():                                        #Defines a function named load_policies
    policies = {}                                           #Creates an empty dictionary.
    policy_dir = "policies"                                 #This is the folder name where your files exist.
    for filename in os.listdir(policy_dir):                 #os.listdir(policy_dir) → gives all files in the folder. Loop runs once per file
        if filename.endswith(".txt"):                       #Only process .txt files
            filepath = os.path.join(policy_dir, filename)   #Builds full path:
            with open(filepath, "r") as f:                  #Opens the file in read mode
                policies[filename] = f.read()               #Reads full file content and stores it in dictionary
    return policies                                         #Returns the final dictionary

policies = load_policies()
print(f"Loaded policies: {list(policies.keys())}")

# ─── search policies for relevant content ───────────────────────────────────

def search_policies(question: str) -> str:
    question_lower = question.lower()
    relevant = []

    # keywords to match each policy
    keywords = {
        "privacy_policy.txt": [
            "privacy", "data", "personal", "information",
            "cookie", "share", "store", "collect", "delete"
        ],
        "exchange_policy.txt": [
            "return", "exchange", "refund", "damaged",
            "shipping", "replace", "policy", "days", "item"
        ]
    }

    for filename, content in policies.items():
        file_keywords = keywords.get(filename, [])
        if any(keyword in question_lower for keyword in file_keywords):
            relevant.append(f"=== {filename} ===\n{content}")

    # if nothing matched, include all policies
    if not relevant:
        relevant = [f"=== {name} ===\n{content}"
                for name, content in policies.items()]

    return "\n\n".join(relevant)

# ─── conversation history per session ───────────────────────────────────────

conversation_history = []

# ─── routes ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "Chatbot is running!"}

# @app.post("/chat")
# def chat(message: Message):
#     # find relevant policy content
#     relevant_policies = search_policies(message.question)

#     # build system prompt with policy context
#     system_prompt = f"""You are a helpful customer support assistant.
# Answer questions ONLY based on the company policies provided below.
# If the answer is not in the policies, say "I'm sorry, I don't have 
# information about that. Please contact our support team."
# Be friendly, concise and helpful.

# COMPANY POLICIES:
# {relevant_policies}
# """

#     # add user message to history
#     conversation_history.append({
#         "role": "user",
#         "content": message.question
#     })

#     try:
#         response = client.messages.create(
#             model="claude-haiku-4-5-20251001",
#             max_tokens=512,
#             system=system_prompt,
#             messages=conversation_history
#         )

#         answer = response.content[0].text

#         # add assistant response to history
#         conversation_history.append({
#             "role": "assistant",
#             "content": answer
#         })

#         return {
#             "answer": answer,
#             "policies_searched": list(policies.keys())
#         }

#     except Exception as e:
#         return {"error": str(e)}

@app.post("/chat")
def chat(message: Message):

    # combine ALL policies together — let claude figure out what's relevant
    all_policies = "\n\n".join([
        f"=== {filename} ===\n{content}"
        for filename, content in policies.items()
    ])

    system_prompt = f"""You are a helpful customer support assistant.
Answer questions ONLY based on the company policies provided below.
If the answer is not in the policies, say "I'm sorry, I don't have
information about that. Please contact our support team."
Be friendly, concise and helpful.

COMPANY POLICIES:
{all_policies}
"""

    conversation_history.append({
        "role": "user",
        "content": message.question
    })

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=system_prompt,
            messages=conversation_history
        )

        answer = response.content[0].text

        conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}
    
@app.get("/history")
def get_history():
    return {"history": conversation_history}

@app.delete("/clear")
def clear_history():
    conversation_history.clear()
    return {"status": "History cleared!"}

@app.get("/policies")
def get_policies():
    return {"policies": list(policies.keys())}