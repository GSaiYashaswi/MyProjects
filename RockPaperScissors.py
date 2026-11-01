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

# Initialize MediaPipe HandLandmarker (Modern API)
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.8,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.9
)
detector = vision.HandLandmarker.create_from_options(options)

def get_user_move(landmarks):
    """Detect Rock, Paper, or Scissors using strict finger pattern matching."""
    tip_ids = [8, 12, 16, 20] # Index, Middle, Ring, Pinky tips
    pip_ids = [6, 10, 14, 18] # Corresponding lower joints
    fingers = []

    # Check the 4 main fingers (1 for open, 0 for closed)
    for tip, pip in zip(tip_ids, pip_ids):
        if landmarks[tip].y < landmarks[pip].y:
            fingers.append(1)  # Open finger
        else:
            fingers.append(0)  # Closed finger

    total_fingers = sum(fingers)

    # Precise Pattern Matching:
    # Index [0] and Middle [1] open, Ring [2] and Pinky [3] closed = Scissors
    if fingers == [1, 1, 0, 0]:
        return "Scissors", total_fingers
    # 3 or more fingers open = Paper
    elif total_fingers >= 3:
        return "Paper", total_fingers
    # 0 or 1 finger open (like a closed fist) = Rock
    elif total_fingers <= 1:
        return "Rock", total_fingers
    
    # Fallback for any other combination
    return "Unknown", total_fingers

# Start Camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Game variables
user_score = 0
comp_score = 0
game_state = "WAITING"
timer_start = 0
user_move = None
comp_move = None
result_text = ""
last_timestamp_ms = 0
last_valid_gesture = "rock"  # Remembers your last steady hand pose

print("Game ready! Press 'SPACE' to start a round. Press 'Q' to quit.")
speak("Welcome to Rock Paper Scissors! Press spacebar to start.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

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

    # Detect hand landmarks using the modern API
    detection_result = detector.detect_for_video(mp_image, timestamp_ms)

    current_user_gesture = None
    finger_count = 0

    if detection_result.hand_landmarks:
        for hand_landmarks in detection_result.hand_landmarks:
            # Draw hand landmark points on the frame
            for lm in hand_landmarks:
                h, w, _ = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)
            
            current_user_gesture, finger_count = get_user_move(hand_landmarks)
            
            # Continuously update our memory of your last clear gesture
            if current_user_gesture and current_user_gesture != "Unknown":
                last_valid_gesture = current_user_gesture

    # UI Overlay - Score
    cv2.putText(frame, f"Score - You: {user_score} | CPU: {comp_score}", (10, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    current_time = time.time()

    if game_state == "WAITING":
        cv2.putText(frame, "Press 'SPACE' to Play", (180, 240), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        if current_user_gesture:
            cv2.putText(frame, f"Move: {current_user_gesture} (Fingers: {finger_count})", (10, 460), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    elif game_state == "COUNTDOWN":
        elapsed = int(current_time - timer_start)
        countdown = 3 - elapsed

        if countdown > 0:
            cv2.putText(frame, str(countdown), (280, 250), 
                        cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 4)
        else:
            # Lock in user move using our reliable memory buffer instead of risking a single-frame drop
            user_move = last_valid_gesture

            comp_move = random.choice(["Rock", "Paper", "Scissors"])

            # Determine winner
            if user_move == comp_move:
                result_text = "It's a Tie!"
            elif (user_move == "Rock" and comp_move == "Scissors") or \
                 (user_move == "Paper" and comp_move == "Rock") or \
                 (user_move == "Scissors" and comp_move == "Paper"):
                result_text = "You Win!"
                user_score += 1
            else:
                result_text = "Computer Wins!"
                comp_score += 1

            # Speak results out loud
            speech_announcement = f"I chose {comp_move}. {result_text}"
            speak(speech_announcement)

            game_state = "RESULT"
            timer_start = time.time()

    elif game_state == "RESULT":
        cv2.putText(frame, f"You: {user_move}", (50, 180), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"CPU: {comp_move}", (400, 180), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, result_text, (200, 260), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

        # Show result for 3 seconds before returning to WAITING
        if current_time - timer_start > 3.0:
            game_state = "WAITING"

    cv2.imshow("Rock Paper Scissors AI", frame)

    # Key Press Handler
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord(' ') and game_state == "WAITING":
        game_state = "COUNTDOWN"
        timer_start = time.time()
        speak("3, 2, 1, Show your move!")

cap.release()
cv2.destroyAllWindows()