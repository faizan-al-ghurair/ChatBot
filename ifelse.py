# If / else
score = 85

if score >= 90:
    print("Grade: A")
elif score >= 80:
    print("Grade: B")
elif score >= 70:
    print("Grade: C")
else:
    print("Grade: F")

# For loop
languages = ["JavaScript", "Python", "Rust", "Go"]

for lang in languages:
    if lang == "Python":
        print(f"{lang} - this is my AI language!")
    else:
        print(f"{lang} - I know this one")

# Range loop
for i in range(5):
    print(f"Step {i}")

# While loop
count = 0
while count < 3:
    print(f"Count is {count}")
    count += 1

# Loop with index
for index, lang in enumerate(languages):
    print(f"{index + 1}. {lang}")