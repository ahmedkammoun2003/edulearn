# PDF Chat Application

## Overview

The PDF Chat Application is a desktop application built using PyQt5 that allows users to upload a PDF file, extract its text, and interact with an AI model to create a text-based educational RPG game based on the content of the PDF.

## Features

- Upload PDF files and extract text content.
- Generate a game prompt from the extracted text.
- Chat with an AI assistant to create an interactive RPG experience.
- Progress bar to indicate loading status during operations.

## Requirements

To run this application, you need to have the following Python packages installed:

- PyMuPDF
- requests
- Flask
- PyQt5

You can install the required packages using pip:

```bash
pip install -r requirements.txt
```

## Usage

1. Clone the repository or download the source code.
2. Install the required packages as mentioned above.
3. Run the application:

```bash
python src/desktop_app.py
```

4. Click on the "Upload PDF" button to select a PDF file.
5. After the file is uploaded, you can interact with the AI assistant by typing your messages in the input area and clicking "Send".

## API Endpoint

The application communicates with the Ollama API for generating responses. Ensure that the Ollama API is running locally at `http://localhost:11434/api/chat`. you just need to download the ollama app locally and the endpoint will work