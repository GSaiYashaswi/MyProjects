import speech_recognition as sr

def listen_speech():
    # Initialize the recognizer
    recognizer = sr.Recognizer()
    
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("\n[LISTENING...] Adjusting for noise and listening. Speak now!")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            # Listen for audio (timeout after 5 seconds of silence)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=30)
            print("Processing speech...")
            
            # Convert speech to text using Google's API
            text = recognizer.recognize_google(audio)
            print(f"\n✨ Transcribed Text: {text}")
            
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected (timed out).")
        except sr.UnknownValueError:
            print("❓ Could not understand the audio.")
        except sr.RequestError as e:
            print(f"❌ Could not request results from service; {e}")

def main():
    print("=" * 40)
    print(" Speech-to-Text Toggle Program ")
    print("=" * 40)
    print("Commands:")
    print("  - Type 'on'  to turn the microphone ON and speak")
    print("  - Type 'off' to EXIT the program")
    print("-" * 40)

    while True:
        # Toggle control prompt
        choice = input("\nEnter command ('on' or 'off'): ").strip().lower()
        
        if choice in ['off', 'exit', 'quit']:
            print("Exiting program. Goodbye!")
            break
        elif choice == 'on':
            listen_speech()
        else:
            print("⚠️ Invalid command. Please type 'on' to listen or 'off' to exit.")

if __name__ == "__main__":
    main()