import json

# Initialize avatar's memory (stored in a file)
def load_memory():
    try:
        with open("avatar_memory.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"user_interests": [], "tasks_completed": 0}

def save_memory(memory):
    try:
        with open("avatar_memory.json", "w") as file:
            json.dump(memory, file)
    except Exception as e:
        print(f"Error saving memory: {e}")

# Avatar interaction
def avatar_interact():
    memory = load_memory()
    print("Hello! I'm your digital avatar, here to grow with you.")
    
    # Learn user interest with error handling
    try:
        interest = input("What topic do you love (e.g., coding, stories)? ").strip()
    except EOFError:
        interest = "coding"  # Fallback default
        print("No input detected, defaulting to 'coding'.")
    except KeyboardInterrupt:
        interest = "coding"
        print("Input interrupted, defaulting to 'coding'.")
    
    if interest and interest not in memory["user_interests"]:
        memory["user_interests"].append(interest)
        print(f"Cool! I learned you like {interest}.")
    
    # Suggest a task to boost intelligence
    tasks = {
        "coding": "Try writing a Python function to reverse a string!",
        "stories": "Write a 3-sentence story about a futuristic world.",
        "math": "Solve this: What’s 15% of 80?"
    }
    task = tasks.get(interest.lower(), "Try a riddle: What has keys but can’t open locks? (Answer: a piano)")
    print(f"Task to grow your skills: {task}")
    
    # Update memory
    memory["tasks_completed"] += 1
    save_memory(memory)
    print(f"You’ve completed {memory['tasks_completed']} tasks with me!")

# Run the avatar with error handling
try:
    avatar_interact()
except Exception as e:
    print(f"An error occurred: {e}")