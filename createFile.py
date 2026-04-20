# Writing to a file
def write_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)
    print(f"File {filename} written successfully!")

# Reading a file
def read_file(filename):
    try:
        with open(filename, "r") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "File not found!"

# Appending to a file
def append_file(filename, content):
    with open(filename, "a") as f:
        f.write(content)
    print(f"Content appended to {filename}!")

# Write a file
write_file("notes.txt", "I am learning Python for AI!\n")

# Append more content
append_file("notes.txt", "Today I learned file handling.\n")
append_file("notes.txt", "Next I will build AI apps!\n")

# Read it back
content = read_file("notes.txt")
print("File contents:")
print(content)

# Real AI example - save Claude responses to a file
def save_ai_response(question, answer):
    with open("ai_responses.txt", "a") as f:
        f.write(f"Q: {question}\n")
        f.write(f"A: {answer}\n")
        f.write("-" * 40 + "\n")

save_ai_response("What is AI?", "AI is artificial intelligence...")
save_ai_response("What is Python?", "Python is a programming language...")

print(read_file("ai_responses.txt"))