import speech_recognition as sr

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as sources:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(sources)

    try:
        print("Recognizing")
        query = r.recognize_google(audio, language='en-uk')
    except Exception as e:
        print(e)
        return "-"
    return query