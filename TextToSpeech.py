import pyttsx3

def text_to_speech(text):
    # Initialize the TTS engine
    engine = pyttsx3.init()
    
    # Optional: Adjust speech rate (speed) and volume
    engine.setProperty('rate', 200)    # Speed of speech (default is usually around 200)
    engine.setProperty('volume', 1.0)  # Volume ranges from 0.0 to 1.0

    print(f"Converting text to speech: '{text}'")
    
    # Queue the text to be spoken
    engine.say(text)
    
    # Process and play the speech audio
    engine.runAndWait()
    print("Finished speaking!")




if __name__ == "__main__":
    message = "im sai yashaswi"
    text_to_speech(message)






