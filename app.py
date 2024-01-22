import g4f
import re
import sys
import asyncio
import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from head.listen import take_command
from head.speak import speak
from bot import sample_generate_text_image_content
from qasync import QEventLoop, asyncSlot

messages = {"role": "system", "content": "you're coded by Mohammed Anas, and Google didn't develop you"},
{"role": "system", "content": "Use modules like webbrowser, pyautogui, time, pyperclip, random, mouse, wikipedia, keyboard, datetime, tkinter, PyQt5, etc."},
{"role": "system", "content": "Don't use the input function and subprocess in Python code"},
{"role": "system", "content": "*Always use default paths in Python code*"},
{"role": "system","content": "When the user says 'show image,' use the following code to display the image:\n```python\nfrom PIL import Image\n\nimage_path = r'output/0.jpeg'\nimage = Image.open(image_path)\nimage.show()\n```\nIf you want to show another image, let me know."},
{"role": "system", "content": "When the user says 'generate an image'or 'create an image' and provides a prompt like 'generate an image about a horse,' extract the prompt from the user query. Then, give this code to the user:\n```python\nfrom cookies.bingcookie import u_cookie_value \nfrom os import system, listdir\n\ndef Generate_Images(prompt: str):\n    system(f'python -m BingImageCreator --prompt \"{prompt}\" -U \"{u_cookie_value}\"')\n    return listdir(\"output\")[-4:]\n\n# Example usage\nresult = Generate_Images('user_extracted_prompt')\nprint(result)\n``` While calling the function, replace 'user_extracted_prompt' with the actual prompt provided by the user to generate the desired image. Just acknowledge the request with 'Ok, sir, generating an image about the user's prompt.' and provide the code."
    },
{"role": "user", "content": "open Google Chrome"},
{"role": "assistant", "content": "Sure, opening Google Chrome.```python\nimport webbrowser\nwebbrowser.open('https://www.google.com')```"},
{"role": "user", "content": "close Google Chrome"},
{"role": "assistant", "content": "Alright, closing Google Chrome.```python\nimport os\nos.system('taskkill /F /IM chrome.exe')```"}


class MainWindow(QWidget):
    def __init__(self, loop=None):
        super().__init__()
        self.initUI()

        # Webcam feed update interval
        self.update_interval = 500  # milliseconds

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_webcam_feed)
        self.timer.start(self.update_interval)

        self.loop = loop or asyncio.get_event_loop()

    def initUI(self):
        hbox = QHBoxLayout(self)

        webcam_frame = QFrame(self)
        webcam_frame.setFrameShape(QFrame.StyledPanel)

        self.label = QLabel(webcam_frame)
        self.label.setGeometry(0, 0, 640, 480)

        bottom = QFrame()
        bottom.setFrameShape(QFrame.StyledPanel)

        self.textedit = QTextEdit()
        self.textedit.setFontPointSize(16)
        button = QPushButton("Start Listening", self)

        splitter2 = QSplitter(Qt.Vertical)
        splitter2.addWidget(self.textedit)
        splitter2.addWidget(button)

        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(webcam_frame)
        splitter1.addWidget(splitter2)
        splitter1.setSizes([400, 400])

        hbox.addWidget(splitter1)
        self.setLayout(hbox)
        QApplication.setStyle(QStyleFactory.create('Cleanlooks'))
        self.setGeometry(100, 100, 1280, 480)
        self.setWindowTitle('Jarvis - Virtual Assistant')
        button.clicked.connect(self.capture_image_async)

    @asyncSlot()
    async def capture_image_async(self):
        try:
            ret, frame = cap.read()
            if ret:
                encoded_frame = cv2.imencode('.jpg', frame)[1].tobytes()
                text = take_command()
                lines = text.splitlines()
                last_line = lines[-1]
                self.textedit.append(f"You: {text}")
                response = await sample_generate_text_image_content(last_line, encoded_frame)
                self.textedit.append(f"GPT: {response}")
                speak(response)
                return response
        except Exception as e:
            print(e)

    def update_webcam_feed(self):
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(frame))

    @staticmethod
    def GPT(*args):
        global messages
        assert args != ()

        message = ''
        for i in args:
            message += i

        messages.append({'role': 'user', "content": message})

        response = g4f.ChatCompletion.create(
            model="gpt-4-32k-0613",
            provider=g4f.Provider.GptGo,
            messages=messages,
            stream=True
        )
        ms = ""
        for i in response:
            ms += i
            print(i, end="", flush=True)

        messages.append({'role': 'assistant', "content": ms})
        return ms

    @staticmethod
    def find_code(text):
        pattern = r'```python(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            code = matches[0].strip()
            return code
        else:
            print('no code found')

        while True:
            query = take_command()
            if query != '-':
                print('user: ' + query)
                response = MainWindow.GPT(query)
                python_code = MainWindow.find_code(response)

                if python_code:
                    response = response.replace(python_code, '').replace(
                        'python', '').replace('```', '')
                    speak(response)
                    exec(python_code)
                else:
                    speak(response)
            else:
                pass

def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = MainWindow(loop)
    window.show()
    speak("Initializing program...")
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    main()
