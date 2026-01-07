import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time, random, csv, os
import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
import Levenshtein
from datetime import datetime

# ================= CONFIG =================
CSV_FILE = "english_cognitive_results.csv"

# English-only Screening Flow
SCREENING_TASKS = [
    {"stage": "Reading", "prompt": "The quick brown fox jumps over the lazy dog"},
    {"stage": "Reading", "prompt": "She is playing with a colorful ball"},
    {"stage": "Numbers", "prompt": "17 71 59"},
    {"stage": "Math", "prompt": "What is five plus three?"},
    {"stage": "Math", "prompt": "What is ten minus four?"}
]

# Initialize Optimized Whisper Model
print("Initializing Speech Engine... (English Optimized)")
# 'base' model is perfect for English; 'int8' makes it run fast on any CPU
model = WhisperModel("base", device="cpu", compute_type="int8")

class EnglishCognitiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("English Cognitive Screening (Ages 5-11)")
        self.root.geometry("850x750")
        
        self.current_step = 0
        self.scores = []
        
        self.build_ui()

    def build_ui(self):
        # Header
        tk.Label(self.root, text="English Voice Screening Tool", font=("Helvetica", 22, "bold"), fg="#2c3e50").pack(pady=20)
        
        # User Configuration Frame
        config_frame = tk.LabelFrame(self.root, text="Student Profile", padx=20, pady=10)
        config_frame.pack(pady=10, padx=30, fill="x")
        
        tk.Label(config_frame, text="Subject ID:").grid(row=0, column=0, sticky="w")
        self.sid_entry = ttk.Entry(config_frame, width=15)
        self.sid_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(config_frame, text="Age (5-11):").grid(row=0, column=2, sticky="w")
        self.age_spin = ttk.Spinbox(config_frame, from_=5, to=11, width=5)
        self.age_spin.set(7)
        self.age_spin.grid(row=0, column=3, padx=10, pady=5)

        # Main Task Area
        self.display_box = tk.Frame(self.root, bg="white", highlightbackground="#dcdde1", highlightthickness=1)
        self.display_box.pack(pady=20, padx=40, fill="x")
        
        self.stage_label = tk.Label(self.display_box, text="Ready to start", font=("Helvetica", 12), bg="white", fg="#7f8c8d")
        self.stage_label.pack(pady=(10, 0))
        
        self.prompt_text = tk.Label(self.display_box, text="Please enter ID and click Start", 
                                    font=("Helvetica", 20, "bold"), wraplength=600, bg="white", pady=30)
        self.prompt_text.pack()

        # Recording Controls
        self.btn_record = ttk.Button(self.root, text="🎤 Start Recording", command=self.handle_action)
        self.btn_record.pack(pady=10)
        
        # Log Output
        self.log = tk.Text(self.root, height=12, font=("Consolas", 10), bg="#fdfdfd", fg="#34495e")
        self.log.pack(fill="both", padx=20, pady=10)

    # --- Screening Logic ---
    def handle_action(self):
        if not self.sid_entry.get():
            messagebox.showwarning("Incomplete", "Please enter a Subject ID")
            return
        
        if self.current_step < len(SCREENING_TASKS):
            self.btn_record.config(state="disabled")
            threading.Thread(target=self.run_task).start()
        else:
            self.reset_screening()

    def run_task(self):
        task = SCREENING_TASKS[self.current_step]
        
        # UI Update
        self.stage_label.config(text=f"Task {self.current_step + 1} of {len(SCREENING_TASKS)}: {task['stage']}")
        self.prompt_text.config(text=task['prompt'], fg="#2980b9")
        
        # 1. Capture High-Quality Audio
        filename = "capture_en.wav"
        self.log.insert(tk.END, f"\n[Listening for {task['stage']}...]\n")
        self.record_audio(filename, duration=6)
        
        # 2. Transcription
        try:
            # We strictly enforce English to prevent cross-language hallucinations
            segments, _ = model.transcribe(filename, language="en", beam_size=5)
            spoken = " ".join([s.text for s in segments]).strip().lower()
            target = task['prompt'].lower()
            
            # 3. Scoring (Levenshtein Ratio + Key Term Matching)
            # Use ratio for reading, but check for specific digits for math
            accuracy = Levenshtein.ratio(target, spoken) * 100
            self.scores.append(accuracy)
            
            self.log.insert(tk.END, f"Target: {target}\nDetected: {spoken}\nAccuracy: {accuracy:.1f}%\n")
            self.log.see(tk.END)
            
        except Exception as e:
            self.log.insert(tk.END, f"Error: {e}\n")
            self.scores.append(0)

        self.current_step += 1
        
        if self.current_step == len(SCREENING_TASKS):
            self.finalize_results()
        else:
            self.btn_record.config(state="normal", text="🎤 Next Question")
            self.prompt_text.config(text="Great! Ready for next?", fg="#2ecc71")

    def record_audio(self, name, duration=6):
        fs = 16000 # Whisper models are trained on 16kHz
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        write(name, fs, recording)

    def finalize_results(self):
        avg_score = sum(self.scores) / len(self.scores)
        
        # Heuristic Assessment
        status = "Normal"
        if avg_score < 75: status = "Borderline - Suggest Retest"
        if avg_score < 60: status = "Risk Detected - Professional Evaluation Recommended"
        
        self.prompt_text.config(text=f"Screening Complete!\nResult: {status}", fg="#c0392b" if avg_score < 60 else "#27ae60")
        self.btn_record.config(state="normal", text="🔄 New Student")
        
        self.log.insert(tk.END, f"\n--- FINAL ASSESSMENT ---\n")
        self.log.insert(tk.END, f"Overall Accuracy: {avg_score:.2f}%\n")
        self.log.insert(tk.END, f"Status: {status}\n")
        
        self.save_to_csv(avg_score, status)

    def save_to_csv(self, final_score, label):
        exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if not exists:
                w.writerow(["SubjectID", "Age", "AverageAccuracy", "FinalLabel", "Timestamp"])
            w.writerow([self.sid_entry.get(), self.age_spin.get(), f"{final_score:.2f}", label, datetime.now().strftime("%Y-%m-%d %H:%M")])

    def reset_screening(self):
        self.current_step = 0
        self.scores = []
        self.log.delete('1.0', tk.END)
        self.prompt_text.config(text="Ready for new screening", fg="black")
        self.btn_record.config(text="🎤 Start Recording")

if __name__ == "__main__":
    root = tk.Tk()
    app = EnglishCognitiveApp(root)
    root.mainloop()