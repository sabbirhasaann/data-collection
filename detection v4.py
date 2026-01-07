import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time, random, csv, os
import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
from banglaspeech2text import Speech2Text
import Levenshtein
from datetime import datetime

# ================= CONFIG =================
CSV_FILE = "cognitive_results_auto.csv"

# Structured Flow: [Stage Name, Prompt, Language Type]
SCREENING_FLOW = [
    ["Bangla_Reading", "আমি আজ স্কুলে যাব", "bn"],
    ["Bangla_Math", "১৫ ৫১", "bn"],
    ["English_Reading", "The boy is reading a book", "en"],
    ["English_Math", "4 plus 5", "en"]
]

# ================= ENGINES =================
print("Initializing AI Models... (This may take a moment)")
en_engine = WhisperModel("base", device="cpu", compute_type="int8")
bn_engine = Speech2Text("base") 

class AutoCognitiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto-Detect Cognitive Screening")
        self.root.geometry("800x700")
        
        self.current_step = 0
        self.results = {}
        self.is_recording = False
        
        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="Automated Cognitive Screening", font=("Arial", 20, "bold")).pack(pady=15)
        
        # Subject ID
        id_frame = tk.Frame(self.root)
        id_frame.pack(pady=10)
        tk.Label(id_frame, text="Enter Subject ID:").pack(side="left")
        self.sid_entry = ttk.Entry(id_frame)
        self.sid_entry.pack(side="left", padx=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Main Task Display
        self.task_box = tk.Frame(self.root, bg="#f9f9f9", bd=2, relief="groove")
        self.task_box.pack(pady=20, padx=50, fill="x")
        
        self.step_label = tk.Label(self.task_box, text="Step 1 of 4", font=("Arial", 10), bg="#f9f9f9")
        self.step_label.pack(pady=5)
        
        self.prompt_display = tk.Label(self.task_box, text="Click Start to Begin Bengali Test", 
                                       font=("Arial", 18, "bold"), wraplength=500, bg="#f9f9f9", fg="#2c3e50")
        self.prompt_display.pack(pady=20)

        # Controls
        self.action_btn = ttk.Button(self.root, text="🎤 Start Recording", command=self.handle_click)
        self.action_btn.pack(pady=10)

        self.log = tk.Text(self.root, height=12, font=("Consolas", 10), bg="#2c3e50", fg="white")
        self.log.pack(fill="both", padx=20, pady=10)

    def handle_click(self):
        if not self.sid_entry.get():
            messagebox.showwarning("ID Required", "Please enter a Subject ID first.")
            return
        
        if self.current_step < len(SCREENING_FLOW):
            self.action_btn.config(state="disabled")
            threading.Thread(target=self.run_screening_step).start()
        else:
            self.reset_app()

    def run_screening_step(self):
        step_name, prompt, lang_type = SCREENING_FLOW[self.current_step]
        
        # Update UI
        self.step_label.config(text=f"Test Stage: {step_name.replace('_', ' ')}")
        self.prompt_display.config(text=f"SAY THIS:\n\n{prompt}")
        self.progress['value'] = (self.current_step / len(SCREENING_FLOW)) * 100
        
        # 1. Record Audio
        filename = f"temp_{lang_type}.wav"
        self.record_audio(filename)
        
        # 2. Transcription with Auto-Dispatch
        self.log.insert(tk.END, f"\n[Step {self.current_step+1}] Detecting {lang_type.upper()} Speech...\n")
        self.log.see(tk.END)
        
        try:
            if lang_type == "bn":
                recognized_text = bn_engine.recognize(filename)
            else:
                segments, _ = en_engine.transcribe(filename, language="en")
                recognized_text = " ".join([s.text for s in segments]).strip()

            # 3. Fuzzy Scoring
            score = Levenshtein.ratio(prompt.strip(), recognized_text.strip()) * 100
            self.results[step_name] = score
            
            self.log.insert(tk.END, f"Target: {prompt}\nSaid: {recognized_text}\nAccuracy: {score:.1f}%\n")
            
        except Exception as e:
            self.log.insert(tk.END, f"Error: {e}\n")
            self.results[step_name] = 0

        self.current_step += 1
        
        if self.current_step == len(SCREENING_FLOW):
            self.finalize_screening()
        else:
            self.prompt_display.config(text="Great! Click 'Start' for next task.")
            self.action_btn.config(state="normal", text="🎤 Next Task")

    def record_audio(self, name, duration=5):
        fs = 16000
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        write(name, fs, recording)

    def finalize_screening(self):
        self.progress['value'] = 100
        self.prompt_display.config(text="Testing Complete!", fg="green")
        self.action_btn.config(state="normal", text="🔄 Reset Test")
        
        # Aggregate Diagnosis
        avg_bn = (self.results["Bangla_Reading"] + self.results["Bangla_Math"]) / 2
        avg_en = (self.results["English_Reading"] + self.results["English_Math"]) / 2
        
        diagnosis = "Normal"
        if avg_bn < 65 or avg_en < 65:
            diagnosis = "Review Required (Cognitive Lag)"
            
        self.log.insert(tk.END, f"\n=== FINAL REPORT ===\n")
        self.log.insert(tk.END, f"Bengali Performance: {avg_bn:.1f}%\n")
        self.log.insert(tk.END, f"English Performance: {avg_en:.1f}%\n")
        self.log.insert(tk.END, f"Result: {diagnosis}\n")
        
        self.save_csv(diagnosis, avg_bn, avg_en)

    def save_csv(self, diagnosis, bn_score, en_score):
        file_exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if not file_exists:
                w.writerow(["SubjectID", "BN_Avg", "EN_Avg", "Diagnosis", "Timestamp"])
            w.writerow([self.sid_entry.get(), f"{bn_score:.2f}", f"{en_score:.2f}", diagnosis, datetime.now()])

    def reset_app(self):
        self.current_step = 0
        self.results = {}
        self.log.delete('1.0', tk.END)
        self.prompt_display.config(text="Click Start to Begin Bengali Test", fg="#2c3e50")
        self.action_btn.config(text="🎤 Start Recording")
        self.progress['value'] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoCognitiveApp(root)
    root.mainloop()