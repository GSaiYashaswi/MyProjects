import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
import random
import time
import pyttsx3
import threading

print("Initializing Hand Cricket...")

# Automatically download the hand landmarker model file if not present
model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("Downloading AI hand tracking model (one-time setup)...")
    url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
    urllib.request.urlretrieve(url, model_path)
    print("Download complete!")

# Initialize Text-To-Speech engine in a non-blocking thread
def speak(text):
    def run_speech():
        try:
            tts_engine = pyttsx3.init()
            tts_engine.setProperty('rate', 160)
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception as e:
            print("Speech error:", e)
    threading.Thread(target=run_speech, daemon=True).start()

# Initialize MediaPipe HandLandmarker
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)
detector = vision.HandLandmarker.create_from_options(options)

def get_user_runs(landmarks):
    """
    Detect runs from 1 to 10 based on finger counts and gestures.
    """
    tip_ids = [8, 12, 16, 20] # Index, Middle, Ring, Pinky tips
    pip_ids = [6, 10, 14, 18] # Corresponding lower joints
    fingers = []

    for tip, pip in zip(tip_ids, pip_ids):
        if landmarks[tip].y < landmarks[pip].y:
            fingers.append(1)
        else:
            fingers.append(0)

    open_fingers_count = sum(fingers)
    thumb_extended = landmarks[4].x < landmarks[3].x
    total_extended = open_fingers_count + (1 if thumb_extended else 0)

    # 1 to 5 fingers standard mapping
    if open_fingers_count == 4 and thumb_extended:
        return 5
    elif open_fingers_count == 4:
        return 4
    elif open_fingers_count == 3:
        return 3
    elif open_fingers_count == 2:
        return 2
    elif open_fingers_count == 1:
        return 1

    # Extended Gestures for 6, 7, 8, 9, 10:
    if thumb_extended and open_fingers_count == 0:
        return 6
    elif fingers == [1, 0, 0, 0] and not thumb_extended:
        return 7
    elif fingers == [1, 1, 0, 0]:
        return 8
    elif fingers == [1, 1, 1, 0]:
        return 9
    elif open_fingers_count >= 4:
        return 10

    return max(1, min(10, total_extended))

# Bulletproof Camera Initialization
print("Opening camera...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Trying camera index 1...")
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Trying default fallback backend...")
    cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ ERROR: Could not open any camera! Please check your webcam connection.")
    input("Press Enter to exit...")
    exit()

print("✅ Camera opened successfully! Starting game window...")

# Game variables
total_score = 0
game_state = "WAITING"
timer_start = 0
user_runs = 0
comp_runs = 0
result_text = ""
last_timestamp_ms = 0
last_valid_runs = 1

speak("Welcome to Hand Cricket 1 to 10 edition! Press spacebar to face a ball.")

try:
    while cap.isOpened():
        ret, frame = cap.read()
        
        # Non-blocking check: Skip and retry if a frame stutters or drops
        if not ret or frame is None:
            time.sleep(0.01)
            continue

        # Flip image horizontally for natural selfie view
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to MediaPipe Image object
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Ensure timestamp is strictly increasing for MediaPipe video mode
        timestamp_ms = int(time.time() * 1000)
        if timestamp_ms <= last_timestamp_ms:
            timestamp_ms = last_timestamp_ms + 1
        last_timestamp_ms = timestamp_ms

        # Detect hand landmarks
        detection_result = detector.detect_for_video(mp_image, timestamp_ms)

        current_runs = 1
        hand_detected = False

        if detection_result.hand_landmarks:
            for hand_landmarks in detection_result.hand_landmarks:
                for lm in hand_landmarks:
                    h, w, _ = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)
                
                current_runs = get_user_runs(hand_landmarks)
                last_valid_runs = current_runs
                hand_detected = True

        # UI Overlay - Score and Title
        cv2.putText(frame, "HAND CRICKET (1 to 10 Batting)", (10, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Total Score: {total_score}", (10, 75), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        current_time = time.time()

        if game_state == "WAITING":
            cv2.putText(frame, "Press 'SPACE' to Play Ball", (150, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            if hand_detected:
                cv2.putText(frame, f"Current Runs: {current_runs}", (10, 450), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        elif game_state == "COUNTDOWN":
            elapsed = int(current_time - timer_start)
            countdown = 3 - elapsed

            if countdown > 0:
                cv2.putText(frame, str(countdown), (280, 250), 
                            cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 4)
            else:
                user_runs = last_valid_runs
                comp_runs = random.randint(1, 10)

                if user_runs == comp_runs:
                    result_text = "OUT! You're Out!"
                    speech_announcement = f"I bowled {comp_runs}. You're out! Final score {total_score} runs."
                    game_state = "GAMEOVER"
                else:
                    total_score += user_runs
                    result_text = f"+{user_runs} Runs!"
                    speech_announcement = f"I bowled {comp_runs}. You scored {user_runs} runs."
                    game_state = "RESULT"

                speak(speech_announcement)
                timer_start = time.time()

        elif game_state == "RESULT":
            cv2.putText(frame, f"You played: {user_runs}", (50, 180), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Bowler: {comp_runs}", (400, 180), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, result_text, (220, 260), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)

            if current_time - timer_start > 2.5:
                game_state = "WAITING"

        elif game_state == "GAMEOVER":
            cv2.putText(frame, f"You: {user_runs} | Bowler: {comp_runs}", (150, 160), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "GAME OVER - OUT!", (160, 220), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            cv2.putText(frame, f"Final Score: {total_score}", (200, 270), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
            cv2.putText(frame, "Press 'SPACE' to Restart | 'Q' to Quit", (110, 340), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

        cv2.imshow("Hand Cricket 1-10 AI", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            if game_state == "WAITING":
                game_state = "COUNTDOWN"
                timer_start = time.time()
                speak("3, 2, 1, Play!")
            elif game_state == "GAMEOVER":
                total_score = 0
                game_state = "COUNTDOWN"
                timer_start = time.time()
                speak("New game! 3, 2, 1, Play!")
except Exception as e:
    print(f"❌ An error occurred during execution: {e}")

cap.release()
cv2.destroyAllWindows()