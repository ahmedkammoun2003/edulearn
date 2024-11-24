import sys
import fitz  # PyMuPDF for PDF text extraction
import requests
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit, QLabel, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal

# Initialize Ollama API endpoint and model
ollama_url = "http://localhost:11434/api/chat"
model_name = "llama3.2"
chat_history = []  # Store chat history globally

# Step 1: Extract Text from PDF
def extract_pdf_text(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Step 2: Create Game Prompt Based on PDF Content
def create_game_prompt(text):
    prompt = f"Turn this information into a text-based educational RPG game with a story: {text[:]}"
    return prompt

class Worker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        pdf_text = extract_pdf_text(self.file_path)
        print("extract")
        game_prompt = create_game_prompt(pdf_text)
        print("created")
        global chat_history
        chat_history = [{"role": "user", "content": game_prompt}]  # Store the initial conversation history
        self.finished.emit("File uploaded successfully. You can now chat!")

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PDF Chat Application')
        layout = QVBoxLayout()

        self.label = QLabel('Upload a PDF file:')
        layout.addWidget(self.label)

        self.upload_button = QPushButton('Upload PDF')
        self.upload_button.clicked.connect(self.upload_pdf)
        layout.addWidget(self.upload_button)

        self.text_area = QTextEdit()
        layout.addWidget(self.text_area)

        self.user_input = QTextEdit()
        layout.addWidget(self.user_input)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setGeometry(100, 100, 400, 300)

    def upload_pdf(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_path:
            self.progress_bar.setRange(0, 0)  # Indeterminate mode
            self.progress_bar.setVisible(True)

            self.worker = Worker(file_path)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()

    def on_finished(self, message):
        self.progress_bar.setVisible(False)
        self.text_area.setText(message)
        self.start_game()  # Start the game after the loading bar ends

    def start_game(self):
        # Use the game prompt created from the PDF content
        if chat_history:
            initial_input = chat_history[0]['content'] + ' Turn this information into a text-based educational RPG game with a story'  # This is the game prompt
            self.chat(initial_input)  # Start the game with the game prompt

    def chat(self, user_input):
        global chat_history
        chat_history.append({"role": "user", "content": user_input})

        # Show loading bar while waiting for the response
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.setVisible(True)

        assistant_response = self.get_ollama_response(chat_history)
        chat_history.append({"role": "assistant", "content": assistant_response})
        self.text_area.append(f"Assistant: {assistant_response}")

        # Hide loading bar after receiving the response
        self.progress_bar.setVisible(False)

    def get_ollama_response(self, history):
        payload = {
            "model": model_name,
            "messages": history
        }
        response = requests.post(ollama_url, json=payload)

        assistant_responses = []
        for line in response.text.splitlines():
            try:
                json_line = json.loads(line)
                if 'message' in json_line and 'content' in json_line['message']:
                    assistant_responses.append(json_line['message']['content'])
            except json.JSONDecodeError:
                print("Error decoding JSON line:", line)

        combined_response = "".join(assistant_responses) if assistant_responses else "No valid responses from Ollama"
        
        if combined_response.strip().isdigit():
            return int(combined_response)
        elif combined_response.lower() in ['true', 'false']:
            return combined_response.lower() == 'true'
        else:
            return combined_response

    def send_message(self):
        user_input = self.user_input.toPlainText()
        if user_input:
            self.chat(user_input)
            self.user_input.clear()  # Clear the input field after sending

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())