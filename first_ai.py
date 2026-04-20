import anthropic

client = anthropic.Anthropic()

user_input = input("Ask Claude anything: ")

message = client.messages.create(
    model="claude-haiku-4-5-20251001",  # 👈 changed this
    max_tokens=256,                      # 👈 and this
    messages=[
        {"role": "user", "content": user_input}
    ]
)

print("\nClaude:", message.content[0].text)