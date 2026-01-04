import cv2
import time

# ---------------- Haar cascade for eyes only ----------------
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

# ---------------- Parameters ----------------
BLINK_FRAMES = 2  # consecutive frames to count as blink
blink_count = 0
eye_closed_counter = 0
last_blink_time = None  # to calculate interval between blinks

# ---------------- Webcam ----------------
cap = cv2.VideoCapture(0)
start_time = time.time()

print("Starting eye blink detection... Press ESC to stop.\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect eyes
    eyes = eye_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    eyes_detected = len(eyes) > 0

    # Draw rectangles for detected eyes
    for ex, ey, ew, eh in eyes:
        cv2.rectangle(frame, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    # Blink detection
    if not eyes_detected:
        eye_closed_counter += 1
    else:
        if eye_closed_counter >= BLINK_FRAMES:
            blink_count += 1
            current_time = time.time() - start_time
            if last_blink_time is not None:
                interval = current_time - last_blink_time
                print(
                    f"Blink #{blink_count} at {current_time:.2f}s, interval since last blink: {interval:.2f}s"
                )
            else:
                print(f"Blink #{blink_count} at {current_time:.2f}s")
            last_blink_time = current_time
        eye_closed_counter = 0

    # Show blink count on webcam
    cv2.putText(
        frame,
        f"Blinks: {blink_count}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        2,
    )

    cv2.imshow("Eye Blink Detector", frame)

    # Stop on ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
