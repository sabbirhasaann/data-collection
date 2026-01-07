import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
import threading
import time, random, csv, os
from datetime import datetime

# ================= CONFIG =================
CSV_FILE = "voice_cognitive_dataset.csv"

bn_sentences = [
    "আমি আজ স্কুলে যাব",
    "বইটা টেবিলের উপর আছে",
    "আমার বন্ধু আমাকে ডাকছে"
]

en_sentences = [
    "The boy is reading a book",
    "She is playing in the garden",
    "I have a red pen"
]

confusing_numbers = ["6 9", "14 41", "15 51", "2 plus 3", "4 plus 5"]

# ================= UTILS =================
def similarity(expected, spoken):
    e = expected.lower().split()
    s = spoken.lower().split()
    match = sum(1 for w in e if w in s)
    return (match / len(e)) * 100 if e else 0

# ================= GUI APP =================
class CognitiveVoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cognitive Voice Screening Tool")
        self.root.geometry("900x600")

        self.recognizer = sr.Recognizer()
        self.stage = "dyslexia"

        self.build_form()

    # ---------- FORM ----------
    def build_form(self):
        tk.Label(self.root, text="Cognitive Voice Screening",font=("Helvetica",24,"bold")).pack(pady=20)

        self.sid = self.entry("Subject ID")
        self.age = self.spin("Age (6-11)",6,11)
        self.lang = self.combo("Language",["Bangla","English"])

        self.task_label = tk.Label(self.root, font=("Helvetica",18), fg="blue")
        self.task_label.pack(pady=20)

        ttk.Button(self.root, text="🎤 Start Recording",command=self.start_recording).pack(pady=10)

        self.output = tk.Text(self.root, height=12, font=("Helvetica",12))
        self.output.pack(fill="both", padx=20)

    def entry(self, label):
        tk.Label(self.root, text=label).pack()
        e = ttk.Entry(self.root)
        e.pack()
        return e

    def spin(self, label,a,b):
        tk.Label(self.root, text=label).pack()
        s = ttk.Spinbox(self.root,from_=a,to=b,width=5)
        s.pack()
        return s

    def combo(self,label,values):
        tk.Label(self.root,text=label).pack()
        c = ttk.Combobox(self.root,values=values,state="readonly")
        c.current(0)
        c.pack()
        return c

    # ---------- RECORD ----------
    def start_recording(self):
        if not self.sid.get():
            messagebox.showerror("Error","Subject ID required")
            return

        threading.Thread(target=self.run_test).start()

    def run_test(self):
        if self.stage == "dyslexia":
            self.dyslexia_score = self.dyslexia_test()
            self.stage = "dyscalculia"
            self.output.insert(tk.END,"\n➡️ Next: Dyscalculia Test\n")
        else:
            self.dyscalculia_score = self.dyscalculia_test()
            self.finish_test()

    # ---------- DYSLEXIA ----------
    def dyslexia_test(self):
        sentence = random.choice(bn_sentences if self.lang.get()=="Bangla" else en_sentences)

        self.task_label.config(text=f"Read aloud:\n{sentence}")
        self.output.insert(tk.END,f"\nReading Task:\n{sentence}\n")

        spoken, duration = self.listen()

        sim = similarity(sentence, spoken)
        score = max(0, sim - duration*5)

        self.output.insert(
            tk.END,f"You said: {spoken}\nDyslexia Score: {score:.1f}%\n"
        )
        return score

    # ---------- DYSCalculia ----------
    def dyscalculia_test(self):
        task = random.choice(confusing_numbers)

        self.task_label.config(text=f"Say this:\n{task}")
        self.output.insert(tk.END,f"\nNumber Task:\n{task}\n")

        spoken, duration = self.listen()

        correct = 100 if task.replace(" ","") in spoken.replace(" ","") else 40
        score = max(0, correct - duration*10)

        self.output.insert(
            tk.END,f"You said: {spoken}\nDyscalculia Score: {score:.1f}%\n"
        )
        return score


    # ---------- VOICE ----------
    def listen(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            start = time.time()
            audio = self.recognizer.listen(source, phrase_time_limit=6)
            duration = time.time() - start
        try:
            text = self.recognizer.recognize_google(
                audio,
                language="bn-BD" if self.lang.get()=="Bangla" else "en-US"
            )
            return text, duration
        except:
            return "", duration

    # ---------- FINAL ----------
    def finish_test(self):
        d1 = self.dyslexia_score
        d2 = self.dyscalculia_score

        if d1 < 60 and d2 < 60:
            label = "Both Dyslexia & Dyscalculia"
        elif d1 < 60:
            label = "Dyslexia"
        elif d2 < 60:
            label = "Dyscalculia"
        else:
            label = "Normal"

        self.output.insert(tk.END,f"\n🧠 FINAL RESULT: {label}\n")
        self.save_csv(label)

        self.stage = "dyslexia"

    # ---------- CSV ----------
    def save_csv(self,label):
        new = not os.path.exists(CSV_FILE)
        with open(CSV_FILE,"a",newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow([
                    "SubjectID",
                    "Age",
                    "Language",
                    "DyslexiaScore",
                    "DyscalculiaScore",
                    "FinalLabel",
                    "Time"
                ])
            w.writerow([
                self.sid.get(), self.age.get(), self.lang.get(),
                round(self.dyslexia_score,2),
                round(self.dyscalculia_score,2),
                label, datetime.now()
            ])

# ================= RUN =================
if __name__ == "__main__":
    root = tk.Tk()
    app = CognitiveVoiceApp(root)
    root.mainloop()