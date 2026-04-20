from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic()

users = [
    {"id": 1, "name": "Faizan", "city": "Dubai"},
    {"id": 2, "name": "John", "city": "London"},
    {"id": 3, "name": "Sara", "city": "New York"},
]

class User(BaseModel):
    name: str
    city: str

class Message(BaseModel):
    question: str

# GET all users
@app.get("/users")
def get_users():
    return {"users": users}

# GET single user
@app.get("/users/{user_id}")
def get_user(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return {"user": user}
    return {"error": "User not found"}

# POST - add new user
@app.post("/users")
def create_user(user: User):
    new_user = {
        "id": len(users) + 1,
        "name": user.name,
        "city": user.city
    }
    users.append(new_user)
    return {"message": "User created!", "user": new_user}

# PUT - update existing user
@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    for i, u in enumerate(users):
        if u["id"] == user_id:
            users[i]["name"] = user.name
            users[i]["city"] = user.city
            return {"message": "User updated!", "user": users[i]}
    return {"error": "User not found"}

# DELETE - remove a user
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    for i, u in enumerate(users):
        if u["id"] == user_id:
            deleted = users.pop(i)
            return {"message": "User deleted!", "user": deleted}
    return {"error": "User not found"}

# POST - ask claude
@app.post("/ask")
def ask_claude(message: Message):
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            system="You are a helpful assistant. Keep answers short and clear.",
            messages=[
                {"role": "user", "content": message.question}
            ]
        )
        answer = response.content[0].text
        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}