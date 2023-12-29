#pip install voice pyttsx3
import pyttsx3
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
x=(input("enter your text :"))    
speak(x)
