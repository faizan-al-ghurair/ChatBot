# api_test.py
import requests
from helpers import greet, clean_text, add_numbers

print(greet("Faizan"))
print(add_numbers(10, 20))
print(clean_text("  HELLO WORLD  "))