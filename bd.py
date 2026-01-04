import cv2
import time
import csv
import os
import numpy as np

# ---------------- Manual Input ----------------
print("=== Participant Information ===")
age = input("Enter Age: ")
gender = input("Enter Gender (Male/Female): ")
task_type = input("Enter Task Type (Reading/Math): ")

# ---------------- CSV Setup ----------------
CSV_FILE = "blink_dataset.csv"


def get_next_subject_id(csv_file):
    if not os.path.exists(csv_file):
        return "S001"
    with open(csv_file, "r") as f:
        rows = list(csv.reader(f))
        if len(rows) <= 1:
            return "S001"
        last_id = rows[-1][0]
        num = int(last_id[1:]) + 1
        return f"S{num:03d}"


SubjectID = get_next_subject_id(CSV_FILE)
write_header = not os.path.exists(CSV_FILE)

# ---------------- Haar Cascades ----------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

# ---------------- Variables ----------------
blink_count = 0
eye_state = "OPEN"
eye_closed_counter = 0
FRAME_TIME = 1 / 30  # Approx FPS
blink_durations = []
blink_intervals = []
last_blink_time = None

# ---------------- Webcam ----------------
cap = cv2.VideoCapture(0)
start_time = time.time()

print("\nFace + Eye Blink Detection Started")
print("Press ESC to stop\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    current_time = time.time() - start_time

    # ---------------- Face Detection ----------------
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    face_detected = len(faces) > 0
    eyes_open = False

    for x, y, w, h in faces:
        # Draw face rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        face_roi_gray = gray[y : y + h, x : x + w]
        face_roi_color = frame[y : y + h, x : x + w]
        eyes = eye_cascade.detectMultiScale(
            face_roi_gray, scaleFactor=1.1, minNeighbors=5
        )
        if len(eyes) > 0:
            eyes_open = True
            # Draw eyes
            for ex, ey, ew, eh in eyes:
                cv2.rectangle(
                    face_roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2
                )

    # ---------------- Blink Logic ----------------
    if face_detected:
        if eyes_open:
            if eye_state == "CLOSED":
                blink_count += 1
                blink_durations.append(eye_closed_counter * FRAME_TIME)

                if last_blink_time is not None:
                    blink_intervals.append(current_time - last_blink_time)
                last_blink_time = current_time
                eye_closed_counter = 0
                eye_state = "OPEN"
        else:
            eye_closed_counter += 1
            eye_state = "CLOSED"
    else:
        eye_state = "OPEN"
        eye_closed_counter = 0

    # ---------------- On-Screen Indicators ----------------
    cv2.putText(
        frame,
        f"{SubjectID}  Blinks: {blink_count}",
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
    )
    cv2.putText(
        frame,
        f"Eye: {eye_state}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),
        2,
    )
    cv2.putText(
        frame,
        f"Time: {current_time:.1f}s",
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2,
    )  # R timer
    cv2.imshow("Face & Eye Blink Monitor", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

# ---------------- Feature Calculation ----------------
task_duration = time.time() - start_time
total_blink_duration = sum(blink_durations)
blink_freq = blink_count / (task_duration / 60) if task_duration > 0 else 0
avg_blink_duration = np.mean(blink_durations) if blink_durations else 0
interblink_mean = np.mean(blink_intervals) if blink_intervals else 0
interblink_std = np.std(blink_intervals) if blink_intervals else 0
blink_variance = np.var(blink_intervals) if blink_intervals else 0
response_time = interblink_mean
attention_score = 1 / (1 + blink_freq) if blink_freq > 0 else 1
# ---------------- Automatic Labeling (Rule-Based) ----------------
# Example rules (can adjust thresholds):
if blink_freq > 30 or interblink_std > 3.0:
    label = "Dyslexia/Dyscalculia"
elif blink_freq < 5:
    label = "Normal"
else:
    label = "Normal"

# ---------------- Save CSV ----------------
header = [
    "SubjectID",
    "Age",
    "Gender",
    "TaskType",
    "BlinkFreq",
    "TotalBlink",
    "AvgBlinkDuration",
    "TotalBlinkDuration",
    "InterBlinkMean",
    "InterBlinkSTD",
    "BlinkVariance",
    "TaskDuration",
    "ResponseTime",
    "AttentionScore",
    "Label",
]

row = [
    SubjectID,
    age,
    gender,
    task_type,
    round(blink_freq, 3),
    blink_count,
    round(avg_blink_duration, 3),
    round(total_blink_duration, 3),
    round(interblink_mean, 3),
    round(interblink_std, 3),
    round(blink_variance, 3),
    round(task_duration, 2),
    round(response_time, 3),
    round(attention_score, 3),
    label,
]

with open(CSV_FILE, "a", newline="") as f:
    writer = csv.writer(f)
    if write_header:
        writer.writerow(header)
    writer.writerow(row)

print(f"\n✅ Data saved for {SubjectID}")
print("Total Blinks Detected:", blink_count)
print("Assigned Label:", label)
print("CSV file:", CSV_FILE)
