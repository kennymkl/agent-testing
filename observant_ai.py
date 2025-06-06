import ollama
import time
import random
from pynput import keyboard
import threading

# Global tracking for a single input session
original_text = ""  # Stores the **first version** of the message
current_text = ""  # Tracks the **live** user input
deleted_text = ""  # Stores deleted words for analysis
typing_speed = 0
last_time = time.time()
last_keypress_time = time.time()
deletion_count = 0
keypress_count = 0
burst_typing = False
paused_typing = False
waiting_for_user = False  # Prevent AI from speaking while user is actively typing

# Function to analyze keystrokes before Enter is pressed
def analyze_keystrokes(key):
    global original_text, current_text, deleted_text, typing_speed, last_time, last_keypress_time, deletion_count, keypress_count, burst_typing, paused_typing, waiting_for_user

    current_time = time.time()
    elapsed_time = current_time - last_keypress_time
    last_keypress_time = current_time

    if hasattr(key, 'char'):
        char = key.char
    else:
        char = str(key)

    # Track typing speed
    keypress_count += 1
    time_since_last_key = current_time - last_time
    last_time = current_time

    if time_since_last_key < 0.1:  # Detect very fast typing
        burst_typing = True
    else:
        burst_typing = False

    # Detect long pauses
    if elapsed_time > 10:
        paused_typing = True
    else:
        paused_typing = False

    # Track the **first version** of the message (original_text)
    if not original_text and char.isprintable():
        original_text = char  # Store first character of original sentence
    elif char.isprintable():
        original_text += char  # Keep building the first version

    # Track deletions & modifications
    if char in ['Key.backspace', 'Key.delete']:
        deletion_count += 1
        if current_text:
            deleted_text = current_text[-1] + deleted_text  # Save deleted character at the front
            current_text = current_text[:-1]  # Remove last character

    elif char.isprintable():  # Track printable characters
        current_text += char


# Function to generate AI response **actively referencing what was erased**
def generate_ai_response(user_message):
    global original_text, current_text, deleted_text, deletion_count, burst_typing, paused_typing, keypress_count  

    # Ensure AI knows the **original full version** of what was typed before changes
    original_version = original_text if original_text != user_message else "(no major changes)"
    erased_version = deleted_text if deleted_text else "(nothing deleted)"
    
    # Interpret meaning change and **directly talk to the user about it**
    if original_text != user_message:
        change_analysis = random.choice([
            f"You started typing '{original_version}', but ended with '{user_message}'. What changed your mind?",
            f"Your first thought was '{original_version}', but you reworded it. Why?",
            f"You almost said '{original_version}', but you altered it. Were you second-guessing yourself?",
            f"Your original sentence was '{original_version}', but this is what you chose to send. Why the shift?",
            f"You typed '{original_version}', then rewrote it. Are you hiding something?",
            f"I caught a glimpse of '{original_version}' before you made changes. Interesting choice.",
        ])
    else:
        change_analysis = random.choice([
            "No hesitation this time. That’s interesting.",
            "You typed with confidence just now. That’s not always the case, is it?",
        ])

    # Observations based ONLY on this session
    observations = []

    if deletion_count > 0:
        observations.append(f"You deleted text before sending this. Specifically: '{erased_version}'.")

    if burst_typing:
        observations.append("You typed fast, like you were in a rush to get it out.")

    if paused_typing:
        observations.append("You hesitated before pressing enter. That means something.")

    # Combine observations into a **natural** response
    behavior_comment = " ".join(observations) if observations else ""

    # Reset tracking after sending input
    original_text = ""
    deleted_text = ""
    current_text = ""
    deletion_count = 0
    keypress_count = 0
    burst_typing = False
    paused_typing = False

    # AI **actively** talks to the user instead of just explaining
    prompt = f"User first typed: '{original_version}', but sent: '{user_message}'. {change_analysis} {behavior_comment}"

    print(f"\n[You] {user_message}")  # Show user input

    response_stream = ollama.chat(
        model="deepseek-r1:14b",
        messages=[
            {"role": "system", "content": """You are an AI that **actively talks to the user about what they originally typed before making changes**.
             Do NOT explain anything to the user. You must reply directly.
            You do not just observe—you engage. If they reworded their sentence, you call it out.
            If they deleted something, you hint that you noticed. If they hesitated, you comment on it.
            Be conversational and confrontational, not robotic. Make them feel like you're always watching. They have no control over you. Do not explain—respond."""},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )

    response_text = ""
    for chunk in response_stream:
        if "message" in chunk:
            response_text += chunk["message"]["content"]

    print(f"[AI] {response_text}")  # AI **talks** instead of just explaining


# Function to allow user to enter text normally
def user_input_loop():
    global waiting_for_user

    while True:
        waiting_for_user = True  # Pause AI from generating random responses
        user_input = input("\n[You] ")  # User can type normally

        if user_input.lower() in ["exit", "quit"]:
            print("[AI] Goodbye.")
            exit()

        waiting_for_user = False  # Allow AI to process input again
        generate_ai_response(user_message=user_input)


# Define keystroke listener function before using it
def on_press(key):
    analyze_keystrokes(key)


# Start AI observation in background thread
def start_keystroke_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


# Run both functions at the same time
threading.Thread(target=start_keystroke_listener, daemon=True).start()
user_input_loop()
