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

# Task Flow: We split these to calculate separate percentages
READING_TASKS = [
    "The boy is reading a book",
    "She is playing in the garden"
]
MATH_TASKS = [
    "17 71 59",
    "Five plus three",
    "Ten minus four"
]

# Combine for the loop
ALL_TASKS = []
for t in READING_TASKS: ALL_TASKS.append({"type": "Dyslexia", "prompt": t})
for t in MATH_TASKS: ALL_TASKS.append({"type": "Math", "prompt": t})

# Initialize Model
print("Loading Speech Engine...")
model = WhisperModel("base", device="cpu", compute_type="int8")

class EnglishCognitiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("English Cognitive Screening")
        self.root.geometry("850x750")
        
        self.current_step = 0
        self.dyslexia_scores = []
        self.math_scores = []
        
        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="English Voice Screening Tool", font=("Helvetica", 22, "bold")).pack(pady=20)
        
        config_frame = tk.LabelFrame(self.root, text="Student Profile", padx=20, pady=10)
        config_frame.pack(pady=10, padx=30, fill="x")
        
        tk.Label(config_frame, text="Subject ID:").grid(row=0, column=0, sticky="w")
        self.sid_entry = ttk.Entry(config_frame, width=15)
        self.sid_entry.grid(row=0, column=1, padx=10)
        
        tk.Label(config_frame, text="Age (5-11):").grid(row=0, column=2, sticky="w")
        self.age_spin = ttk.Spinbox(config_frame, from_=5, to=11, width=5)
        self.age_spin.set(7)
        self.age_spin.grid(row=0, column=3, padx=10)

        self.display_box = tk.Frame(self.root, bg="white", highlightbackground="#dcdde1", highlightthickness=1)
        self.display_box.pack(pady=20, padx=40, fill="x")
        
        self.prompt_text = tk.Label(self.display_box, text="Enter ID and click Start", 
                                    font=("Helvetica", 20, "bold"), wraplength=600, bg="white", pady=40)
        self.prompt_text.pack()

        self.btn_record = ttk.Button(self.root, text="🎤 Start Recording", command=self.handle_action)
        self.btn_record.pack(pady=10)
        
        self.log = tk.Text(self.root, height=12, font=("Consolas", 10), bg="#fdfdfd")
        self.log.pack(fill="both", padx=20, pady=10)

    def handle_action(self):
        if not self.sid_entry.get():
            messagebox.showwarning("Incomplete", "Please enter a Subject ID")
            return
        
        if self.current_step < len(ALL_TASKS):
            self.btn_record.config(state="disabled")
            threading.Thread(target=self.run_task).start()
        else:
            self.reset_screening()

    def run_task(self):
        task = ALL_TASKS[self.current_step]
        self.prompt_text.config(text=task['prompt'], fg="#2980b9")
        
        # 1. Record
        filename = "temp_audio.wav"
        fs = 16000
        recording = sd.rec(int(6 * fs), samplerate=fs, channels=1)
        sd.wait()
        write(filename, fs, recording)
        
        # 2. Transcribe & Score
        try:
            segments, _ = model.transcribe(filename, language="en")
            spoken = " ".join([s.text for s in segments]).strip().lower()
            target = task['prompt'].lower()
            
            score = Levenshtein.ratio(target, spoken) * 100
            
            if task['type'] == "Dyslexia":
                self.dyslexia_scores.append(score)
            else:
                self.math_scores.append(score)
                
            self.log.insert(tk.END, f"[{task['type']}] Result: {score:.1f}%\n")
        except Exception as e:
            self.log.insert(tk.END, f"Error: {e}\n")

        self.current_step += 1
        if self.current_step == len(ALL_TASKS):
            self.finalize_results()
        else:
            self.btn_record.config(state="normal", text="🎤 Next Question")

    def finalize_results(self):
        # Calculate Averages
        d_avg = sum(self.dyslexia_scores) / len(self.dyslexia_scores) if self.dyslexia_scores else 0
        m_avg = sum(self.math_scores) / len(self.math_scores) if self.math_scores else 0
        
        # Final Label Logic
        label = "Normal"
        if d_avg < 70 and m_avg < 70: label = "Both Risk"
        elif d_avg < 70: label = "Dyslexia Risk"
        elif m_avg < 70: label = "Dyscalculia Risk"
        
        self.prompt_text.config(text=f"Test Complete!\nLabel: {label}", fg="#27ae60")
        self.btn_record.config(state="normal", text="🔄 New Test")
        
        # SAVE TO CSV
        self.save_to_csv(d_avg, m_avg, label)
        self.log.insert(tk.END, f"\n[SUCCESS] Saved to {CSV_FILE}\n")

    def save_to_csv(self, d_score, m_score, label):
        file_exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Header matching your requested format
            if not file_exists:
                writer.writerow(["ID", "Age", "Dyslexia%", "Math%", "Label", "Date"])
            
            # Row matching your requested format
            writer.writerow([
                self.sid_entry.get(),
                self.age_spin.get(),
                f"{d_score:.1f}%",
                f"{m_score:.1f}%",
                label,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ])

    def reset_screening(self):
        self.current_step = 0
        self.dyslexia_scores = []
        self.math_scores = []
        self.log.delete('1.0', tk.END)
        self.prompt_text.config(text="Ready for new session", fg="black")
        self.btn_record.config(text="🎤 Start Recording")

if __name__ == "__main__":
    root = tk.Tk()
    app = EnglishCognitiveApp(root)
    root.mainloop()