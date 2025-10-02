import google.generativeai as genai
import base64
import io
import os
from dotenv import load_dotenv    
from PIL import Image
import streamlit as st
from PyPDF2 import PdfReader
from audiorecorder import audiorecorder
import whisper

st.set_page_config(page_title="Ask me anything I'll let you know", layout="centered")
st.title("💬 Gemini General QnA Chatbot")
st.markdown("Type a message to start a conversation!")

load_dotenv()
API_KEY = os.getenv("api_key")

def initialize_gemini_chat():
    """Initializes the Gemini model and chat session."""
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        # Initialize the chat session and store it in session_state
        st.session_state.chat = model.start_chat(history=[])
        # Also initialize a list to store the displayable messages
        st.session_state.messages = []
    except Exception as e:
        st.error(f"Failed to initialize Gemini: {e}")
        st.session_state.chat = None # Set to None if initialization fails

def encode_image_to_base64(image_file):
    try:
        img=Image.open(image_file).convert("RGB")
        img_byte_arr=io.BytesIO()
        img.save(img_byte_arr,format='PNG')
        return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    except Exception as e:
        st.error(f"Error encoding image: {e}")
        return None

def get_choice():
    choice=st.sidebar.radio("Choose:", ["Converse with Gemini 2.5",
                                          "Chat with a PDF",
                                          "Chat with an image",
                                          "Chat with Voice",])
    return choice

def process_prompt(prompt):
    gemini_input = [{"text": prompt}]
    if "current_uploaded_image" in st.session_state and st.session_state.current_uploaded_image:
        base64_img = encode_image_to_base64(st.session_state.current_uploaded_image)
        if base64_img:
            gemini_input.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": base64_img
                }
            })

    # Generate response
    with st.spinner("Thinking..."):
        try:
            # Use the chat object stored in session_state
            response_message = st.session_state.chat.send_message(gemini_input)
            chatbot_response = response_message.text
            # 4. Store and display the assistant message
            st.session_state.messages.append({"role": "assistant", "content": chatbot_response})
            with st.chat_message("assistant"):
                st.markdown(chatbot_response)
            return chatbot_response
        except Exception as e:
            return st.error(f"⚠️ Error: {str(e)}")

def read_pdf(file):
    try:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

def load_model():
    return whisper.load_model("base")

model = load_model()

def transcribe_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        f.flush()
        result = model.transcribe(f.name)
    return result["text"]
    
def main():

    choice = get_choice()
    # --- Streamlit UI Setup ---
    # 1. Initialize chat only on the first run
    if "chat" not in st.session_state or st.session_state.chat is None:
        initialize_gemini_chat()

    if st.session_state.chat is None:
        return # Stop execution if initialization failed

    # --- Display Existing Messages ---
    # This loop ensures that the history is drawn on every re-run
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if choice=="Converse with Gemini 2.5":
        # --- Chat Input and Response ---
        if prompt := st.chat_input("Type your message here..."):
            
            # Store and display the user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Prepare input for Gemini
            process_prompt(prompt)

    if choice=="Chat with an image":
        uploaded_file = st.sidebar.file_uploader("Upload an image (optional)", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            st.session_state.current_uploaded_image = uploaded_file
            st.sidebar.image(uploaded_file, caption="Current Uploaded Image", use_container_width=True)
            st.sidebar.info("Image uploaded. Your next message will include this image.")
            if prompt := st.chat_input("Type your message here..."):
            
            # Store and display the user message
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

            # Prepare input for Gemini
                process_prompt(prompt)

        elif uploaded_file is None and "current_uploaded_image" in st.session_state:
            st.session_state.current_uploaded_image = None
            st.sidebar.info("Image cleared.")
        
    
    if choice=='Chat with a PDF':
        uploaded_file=st.sidebar.file_uploader("Upload Pdf",type=["pdf"],accept_multiple_files=False)
        
        if uploaded_file:
            pdf_text = read_pdf(uploaded_file)
            if pdf_text:
                st.sidebar.success("✅ PDF loaded. Ask about it!")

                if prompt := st.chat_input("Ask something about the PDF..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    # Append PDF context to query
                    process_prompt(f"PDF Content:\n{pdf_text}\n\nUser Question: {prompt}")
    
    if choice == "Chat with Voice":
        st.sidebar.header("🎙️ Voice Input")
        audio = audiorecorder("Start Recording", "Stop Recording")
        if len(audio) > 0:
            st.audio(audio.export().read(), format="audio/wav")
            audio_bytes = audio.export().read()
            user_text = transcribe_audio(audio_bytes)
            if user_text.strip():
                st.session_state.messages.append({"role": "user", "content": f"🎧 {user_text}"})
                with st.chat_message("user"):
                    st.markdown(f"🎧 {user_text}")
                response = process_prompt(user_text)
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)
        

if __name__ == '__main__':
    main()
