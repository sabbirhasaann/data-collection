import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time, random, csv, os
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
import Levenshtein
from datetime import datetime

# ================= CONFIG =================
CSV_FILE = "voice_cognitive_dataset.csv"

# Cognitive tasks
TASKS = {
    "Bangla": ["আমি আজ স্কুলে যাব", "বইটা টেবিলের উপর আছে", "আমার বন্ধু আমাকে ডাকছে"],
    "English": ["The boy is reading a book", "She is playing in the garden", "I have a red pen"]
}
MATH_TASKS = ["6 9", "14 41", "15 51", "2 plus 3", "4 plus 5"]

# Initialize Whisper (using 'base' for speed vs accuracy balance)
# Use "tiny" for very old PCs, "small" for better accuracy.
print("Loading Voice Model... Please wait.")
voice_model = WhisperModel("base", device="cpu", compute_type="int8")

class CognitiveVoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Cognitive Voice Screening")
        self.root.geometry("900x700")
        self.stage = "dyslexia"
        self.is_recording = False
        self.build_ui()

    def build_ui(self):
        # Header
        tk.Label(self.root, text="Voice Screening V2", font=("Helvetica", 22, "bold")).pack(pady=10)
        
        # User Info Frame
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10)
        
        self.sid = self.add_field(info_frame, "Subject ID")
        self.age = self.add_spin(info_frame, "Age", 6, 11)
        self.lang = self.add_combo(info_frame, "Language", ["Bangla", "English"])

        # Display Area
        self.task_label = tk.Label(self.root, text="Press 'Start' to Begin", font=("Helvetica", 16), fg="blue", wraplength=700)
        self.task_label.pack(pady=20)

        # Control Buttons
        self.record_btn = ttk.Button(self.root, text="🎤 Start Task", command=self.toggle_task)
        self.record_btn.pack(pady=10)

        self.output = tk.Text(self.root, height=12, font=("Consolas", 11), bg="#f4f4f4")
        self.output.pack(fill="both", padx=20, pady=10)

    # --- Helper UI Methods ---
    def add_field(self, parent, label):
        tk.Label(parent, text=label).pack(side="left", padx=5)
        e = ttk.Entry(parent, width=10)
        e.pack(side="left", padx=5)
        return e

    def add_spin(self, parent, label, a, b):
        tk.Label(parent, text=label).pack(side="left", padx=5)
        s = ttk.Spinbox(parent, from_=a, to=b, width=5)
        s.pack(side="left", padx=5)
        return s

    def add_combo(self, parent, label, vals):
        tk.Label(parent, text=label).pack(side="left", padx=5)
        c = ttk.Combobox(parent, values=vals, state="readonly", width=10)
        c.current(0)
        c.pack(side="left", padx=5)
        return c

    # --- Core Logic ---
    def toggle_task(self):
        if not self.sid.get():
            messagebox.showwarning("Input Error", "Please enter Subject ID")
            return
        
        threading.Thread(target=self.execute_screening_flow).start()

    def execute_screening_flow(self):
        # Determine task
        current_lang = self.lang.get()
        prompt = random.choice(TASKS[current_lang]) if self.stage == "dyslexia" else random.choice(MATH_TASKS)
        
        self.task_label.config(text=f"PLEASE SAY:\n\n'{prompt}'")
        self.root.update()
        
        # 1. Capture Audio
        audio_file = "temp_capture.wav"
        self.record_audio(audio_file, duration=5)
        
        # 2. Transcribe
        self.output.insert(tk.END, f"\n[Processing {self.stage}...] ")
        spoken_text = self.transcribe_audio(audio_file, current_lang)
        self.output.insert(tk.END, f"Detected: '{spoken_text}'\n")
        
        # 3. Score using Levenshtein Distance
        # Ratio is 0 to 1, where 1 is a perfect match
        score = Levenshtein.ratio(prompt.lower(), spoken_text.lower()) * 100
        
        if self.stage == "dyslexia":
            self.dyslexia_score = score
            self.stage = "dyscalculia"
            self.output.insert(tk.END, f"Dyslexia Accuracy: {score:.1f}%\n")
            self.task_label.config(text="Next: Number/Math Task. Click 'Start' again.")
        else:
            self.dyscalculia_score = score
            self.finalize_results()

    def record_audio(self, filename, duration=5, fs=16000):
        self.record_btn.config(state="disabled", text="🔴 Recording...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        write(filename, fs, recording)
        self.record_btn.config(state="normal", text="🎤 Start Task")

    def transcribe_audio(self, path, lang):
        lang_code = "bn" if lang == "Bangla" else "en"
        segments, _ = voice_model.transcribe(path, language=lang_code, beam_size=5)
        return " ".join([seg.text for seg in segments]).strip()

    def finalize_results(self):
        d1, d2 = self.dyslexia_score, self.dyscalculia_score
        
        # Heuristic Logic
        if d1 < 70 and d2 < 70: result = "High Risk: Both"
        elif d1 < 70: result = "Risk: Dyslexia"
        elif d2 < 70: result = "Risk: Dyscalculia"
        else: result = "Normal Performance"
        
        self.output.insert(tk.END, f"\n--- FINAL ASSESSMENT: {result} ---\n")
        self.save_csv(result)
        self.stage = "dyslexia" # Reset

    def save_csv(self, label):
        exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if not exists:
                w.writerow(["ID", "Age", "Lang", "Dyslexia%", "Math%", "Label", "Date"])
            w.writerow([self.sid.get(), self.age.get(), self.lang.get(), 
                        f"{self.dyslexia_score:.2f}", f"{self.dyscalculia_score:.2f}", 
                        label, datetime.now().strftime("%Y-%m-%d %H:%M")])

if __name__ == "__main__":
    root = tk.Tk()
    app = CognitiveVoiceApp(root)
    root.mainloop()