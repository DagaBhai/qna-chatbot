# Gemini General QnA Chatbot

A Streamlit-based web application that allows users to interact with Google's Gemini 2.5 model for text-based conversations, image analysis, PDF content queries, and voice input transcription. The app supports multiple interaction modes, including text chat, image-based queries, PDF content analysis, and voice-to-text conversations.

## Features
- **Text-based Chat**: Converse directly with the Gemini 2.5 model by typing messages.
- **Image-based Queries**: Upload an image and ask questions about it, leveraging Gemini's vision capabilities.
- **PDF Content Analysis**: Upload a PDF file and ask questions about its content.
- **Voice Input**: Record audio, transcribe it to text, and interact with Gemini using the transcribed text.
- **User-friendly Interface**: Built with Streamlit for a clean and intuitive web-based UI.

## Requirements
To run this application, you need to install the following Python packages. These are listed in the `requirements.txt` file included in the repository.

```
google-generativeai
python-dotenv
Pillow
streamlit
PyPDF2
whisper
sounddevice
numpy
scipy
```

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/DagaBhai/qna-chatbot.git
   cd DagaBhai/qna-chatbot
   ```

2. **Set Up a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory.
   - Add your Google Gemini API key:
     ```
     api_key=your-gemini-api-key
     ```
   - You can obtain an API key from [Google's API Console](https://console.cloud.google.com/).

5. **Install Whisper Model**:
   - The application uses the `tiny` Whisper model for audio transcription. The model is automatically loaded via the `whisper` package.

## Usage
1. **Run the Application**:
   ```bash
   streamlit run app.py
   ```
   Replace `app.py` with the name of your main Python script if different.

2. **Interact with the Chatbot**:
   - Open the application in your browser (usually at `http://localhost:8501`).
   - Use the sidebar to select an interaction mode:
     - **Converse with Gemini 2.5**: Type a message to chat directly with the Gemini model.
     - **Chat with an Image**: Upload a PNG, JPG, or JPEG image and ask questions about it.
     - **Chat with a PDF**: Upload a PDF file and ask questions about its content.
     - **Chat with Voice**: Record audio (8 seconds by default) and interact using transcribed text.
   - Follow the on-screen prompts to upload files or record audio as needed.

3. **Example Interactions**:
   - **Text Chat**: Ask questions like "What is the capital of France?".
   - **Image Chat**: Upload a photo and ask, "What objects are in this image?".
   - **PDF Chat**: Upload a document and ask, "Summarize the main points of this PDF.".
   - **Voice Chat**: Click "Start Recording" to record audio, which will be transcribed and sent to Gemini.

## Project Structure
```
├── app.py              # Main Streamlit application script
├── requirements.txt    # List of required Python packages
├── .env                # Environment file for API keys (not included in repository)
├── README.md           # This file
```

## Notes
- Ensure you have a stable internet connection, as the Gemini API requires online access.
- The Whisper `tiny` model is used for audio transcription to keep the application lightweight. For better transcription accuracy, you can modify the code to use a larger model (e.g., `base` or `small`), but this will increase resource usage.
- Audio recording uses a default duration of 8 seconds and a sample rate of 16kHz. Adjust these parameters in the code if needed.
- The application handles errors gracefully and displays them in the Streamlit interface.

## Troubleshooting
- **API Key Issues**: Verify that your `.env` file contains the correct `api_key` and that the key is valid.
- **Module Not Found**: Ensure all dependencies are installed using `pip install -r requirements.txt`.
- **Audio Issues**: Ensure your system has a microphone and that the `sounddevice` library is properly configured.
- **PDF Errors**: Ensure the uploaded PDF is not corrupted and contains extractable text.

## Acknowledgments
- Built with [Streamlit](https://streamlit.io/) for the web interface.
- Powered by [Google Gemini 2.5](https://cloud.google.com/generative-ai) for conversational and vision capabilities.
- Audio transcription provided by [Whisper](https://github.com/openai/whisper).
