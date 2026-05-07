import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import pyautogui
import requests
import pyperclip
import time
import sys
import urllib.parse
import pywhatkit

# ---------------- CONFIG ----------------
OPENROUTER_API_KEY = "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"
GEMINI_API_KEY = "AIzaSyDYF5pU5ip-z4q9Ve-kmMMKaqrd5c_0v9Y"

AI_URL = "https://openrouter.ai/api/v1/chat/completions"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

OWNER_NAME = "Rishabh Sir"

chat_history = []
internet_cache = {"status": True, "last_check": 0}

# ---------------- VOICE ----------------
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    if not text:
        return
    print("Jarvis:", text)
    try:
        engine.stop()
        engine.say(text)
        engine.runAndWait()
    except:
        print("Voice error")

# ---------------- INTERNET CHECK ----------------
def is_online():
    global internet_cache

    if time.time() - internet_cache["last_check"] < 10:
        return internet_cache["status"]

    try:
        requests.get("https://www.google.com", timeout=2)
        internet_cache["status"] = True
    except:
        internet_cache["status"] = False

    internet_cache["last_check"] = time.time()
    return internet_cache["status"]

# ---------------- LISTEN ----------------
def listen():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("🎤 Listening...")
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio = r.listen(source, timeout=5, phrase_time_limit=7)

        command = r.recognize_google(audio, language="en-IN")
        print("You:", command)
        return command.lower()

    except:
        return ""

# ---------------- AI ----------------
def ask_ai(prompt):
    global chat_history

    if not is_online():
        return "Internet nahi hai"

    chat_history.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": f"You are Jarvis. Owner is {OWNER_NAME}. Reply short Hindi+English."
            }
        ] + chat_history[-5:]
    }

    try:
        res = requests.post(AI_URL, headers=headers, json=data)

        result = res.json()
        reply = result["choices"][0]["message"]["content"]

        chat_history.append({"role": "assistant", "content": reply})
        return reply

    except:
        return "AI error"

# ---------------- GEMINI ----------------
def ask_gemini(prompt):
    headers = {"Content-Type": "application/json"}

    data = {
        "contents": [
            {"parts": [{"text": f"Create detailed image prompt: {prompt}"}]}
        ]
    }

    try:
        res = requests.post(GEMINI_URL, headers=headers, json=data)
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return prompt

# ---------------- IMAGE ----------------
def generate_image(prompt):
    speak("Generating image")

    ai_prompt = ask_gemini(prompt)
    encoded = urllib.parse.quote(ai_prompt)

    url = f"https://image.pollinations.ai/prompt/{encoded}"
    webbrowser.open(url)

    speak("Image ready")

# ---------------- COMMANDS ----------------
def execute(cmd):

    # 🔥 IMAGE FIRST
    if any(x in cmd for x in ["generate image", "create image", "image of", "draw"]):
        prompt = cmd
        for word in ["generate image", "create image", "image of", "draw"]:
            prompt = prompt.replace(word, "")

        generate_image(prompt.strip())
        return

    # 🔥 PLAY VIDEO (FIXED)
    if "play" in cmd:
        video = cmd.replace("play", "").strip()

        if not video:
            speak("Kya play karna hai?")
            return

        speak(f"Playing {video}")
        try:
            pywhatkit.playonyt(video)
        except:
            speak("Video play nahi hua")
        return

    # OWNER
    if "owner" in cmd:
        speak("Mere malik Rishabh Sir hain")

    # TIME
    elif "time" in cmd:
        speak(datetime.datetime.now().strftime("%H:%M"))

    # DATE
    elif "date" in cmd:
        speak(datetime.datetime.now().strftime("%d %B %Y"))

    # OPEN APPS
    elif "open chrome" in cmd:
        os.system("start chrome")

    elif "open notepad" in cmd:
        os.system("notepad")

    elif "open calculator" in cmd:
        os.system("calc")

    # SEARCH
    elif "search" in cmd:
        q = cmd.replace("search", "")
        webbrowser.open(f"https://www.google.com/search?q={q}")

    # YOUTUBE OPEN ONLY
    elif "youtube" in cmd:
        webbrowser.open("https://www.youtube.com")

    # CLIPBOARD
    elif "read clipboard" in cmd:
        speak(pyperclip.paste())

    # VOLUME
    elif "volume up" in cmd:
        pyautogui.press("volumeup", presses=5)

    elif "volume down" in cmd:
        pyautogui.press("volumedown", presses=5)

    # SCREENSHOT
    elif "screenshot" in cmd:
        pyautogui.screenshot().save("screenshot.png")
        speak("Screenshot saved")

    # EXIT
    elif "exit" in cmd or "stop" in cmd:
        speak("Goodbye")
        sys.exit()

    # AI
    else:
        speak(ask_ai(cmd))

# ---------------- MAIN ----------------
def run():
    speak("Jarvis activated Rishabh Sir")

    while True:
        cmd = listen()
        if cmd:
            execute(cmd)

# ---------------- START ----------------
if __name__ == "__main__":
    run()
