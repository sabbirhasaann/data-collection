import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time, random, csv, os
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
from banglaspeech2text import Speech2Text
import Levenshtein
from datetime import datetime

# ================= CONFIG =================
CSV_FILE = "voice_cognitive_dataset.csv"

TASKS = {
    "Bangla": ["আমি আজ স্কুলে যাব", "বইটা টেবিলের উপর আছে", "আমার বন্ধু আমাকে ডাকছে"],
    "English": ["The boy is reading a book", "She is playing in the garden", "I have a red pen"]
}
MATH_TASKS = ["6 9", "14 41", "15 51", "2 plus 3", "4 plus 5"]

# Initialize Models
print("Loading Models... Please wait.")
# Engine 1: Optimized General Whisper for English
en_engine = WhisperModel("base", device="cpu", compute_type="int8")
# Engine 2: Fine-tuned for Bangla (Downloads on first run)
bn_engine = Speech2Text("base") 

class CognitiveVoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bilingual Cognitive Screening (BN/EN)")
        self.root.geometry("900x700")
        self.stage = "dyslexia"
        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="Bilingual Cognitive Screening", font=("Helvetica", 22, "bold")).pack(pady=10)
        
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10)
        
        self.sid = self.add_field(info_frame, "Subject ID")
        self.age = self.add_spin(info_frame, "Age", 6, 11)
        self.lang = self.add_combo(info_frame, "Language", ["Bangla", "English"])

        self.task_label = tk.Label(self.root, text="Select Language & Press 'Start'", font=("Helvetica", 16), fg="blue", wraplength=700)
        self.task_label.pack(pady=20)

        self.record_btn = ttk.Button(self.root, text="🎤 Start Recording", command=self.run_task_thread)
        self.record_btn.pack(pady=10)

        self.output = tk.Text(self.root, height=12, font=("Consolas", 11), bg="#f8f9fa")
        self.output.pack(fill="both", padx=20, pady=10)

    def add_field(self, parent, label):
        tk.Label(parent, text=label).pack(side="left", padx=5)
        e = ttk.Entry(parent, width=10)
        e.pack(side="left", padx=5); return e

    def add_spin(self, parent, label, a, b):
        tk.Label(parent, text=label).pack(side="left", padx=5)
        s = ttk.Spinbox(parent, from_=a, to=b, width=5)
        s.pack(side="left", padx=5); return s

    def add_combo(self, parent, label, vals):
        tk.Label(parent, text=label).pack(side="left", padx=5)
        c = ttk.Combobox(parent, values=vals, state="readonly", width=10)
        c.current(0); c.pack(side="left", padx=5); return c

    # --- Task Flow ---
    def run_task_thread(self):
        if not self.sid.get():
            messagebox.showwarning("Error", "Enter Subject ID"); return
        threading.Thread(target=self.execute_task).start()

    def execute_task(self):
        current_lang = self.lang.get()
        prompt = random.choice(TASKS[current_lang]) if self.stage == "dyslexia" else random.choice(MATH_TASKS)
        
        self.task_label.config(text=f"PLEASE SAY:\n\n'{prompt}'")
        
        # Audio Settings
        temp_file = "current_voice.wav"
        self.record_btn.config(state="disabled", text="🔴 Listening...")
        
        # Capture 5 seconds of audio
        fs = 16000
        duration = 5
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        write(temp_file, fs, recording)
        
        self.record_btn.config(state="normal", text="🎤 Start Next")
        self.output.insert(tk.END, f"\n[Analyzing {current_lang} Speech...]\n")

        # ENGINE SWITCHER
        try:
            if current_lang == "Bangla":
                # Using specialized Bangla Engine
                spoken_text = bn_engine.recognize(temp_file)
            else:
                # Using general English Engine
                segments, _ = en_engine.transcribe(temp_file, language="en")
                spoken_text = " ".join([s.text for s in segments]).strip()

            self.output.insert(tk.END, f"Recognized: {spoken_text}\n")
            
            # Fuzzy Scoring (Levenshtein)
            score = Levenshtein.ratio(prompt.strip(), spoken_text.strip()) * 100
            self.output.insert(tk.END, f"Accuracy: {score:.1f}%\n")

            if self.stage == "dyslexia":
                self.dyslexia_score = score
                self.stage = "dyscalculia"
            else:
                self.dyscalculia_score = score
                self.finalize_results()
                
        except Exception as e:
            self.output.insert(tk.END, f"Error during recognition: {e}\n")

    def finalize_results(self):
        d1, d2 = self.dyslexia_score, self.dyscalculia_score
        label = "Normal"
        if d1 < 65: label = "Dyslexia Risk"
        elif d2 < 65: label = "Dyscalculia Risk"
        if d1 < 65 and d2 < 65: label = "High Risk: Multiple"
        
        self.output.insert(tk.END, f"\n--- ASSESSMENT: {label} ---\n")
        self.save_csv(label)
        self.stage = "dyslexia"

    def save_csv(self, label):
        file_exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["ID", "Age", "Lang", "D-Score", "M-Score", "Result", "Time"])
            writer.writerow([self.sid.get(), self.age.get(), self.lang.get(), 
                             round(self.dyslexia_score,2), round(self.dyscalculia_score,2), 
                             label, datetime.now().strftime("%Y-%m-%d %H:%M")])

if __name__ == "__main__":
    root = tk.Tk()
    app = CognitiveVoiceApp(root)
    root.mainloop()