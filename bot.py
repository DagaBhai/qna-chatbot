import google.generativeai as genai
import base64
import io
import os
import tempfile
from dotenv import load_dotenv 
from PIL import Image
import streamlit as st
from PyPDF2 import PdfReader
import whisper

import sounddevice as sd
import numpy as np
import scipy.io.wavfile

st.set_page_config(page_title="Ask me anything I'll let you know", layout="centered")
st.title("💬 Gemini General QnA Chatbot")
st.markdown("Type a message to start a conversation!")

load_dotenv()
API_KEY = os.getenv("api_key")

def initialize_gemini_chat():
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        st.session_state.chat = model.start_chat(history=[])
        st.session_state.messages = []
    except Exception as e:
        st.error(f"Failed to initialize Gemini: {e}")
        st.session_state.chat = None

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

    with st.spinner("Thinking..."):
        try:
            response_message = st.session_state.chat.send_message(gemini_input)
            chatbot_response = response_message.text
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

def transcribe_audio(audio_data, sample_rate):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        temp_filename = f.name
    
    scipy.io.wavfile.write(temp_filename, sample_rate, audio_data)
    
    try:
        result = model.transcribe(temp_filename)
        return result["text"]
    finally:
        os.unlink(temp_filename)

def record_audio(duration=8, sample_rate=16000):
    st.sidebar.info(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    st.sidebar.success("Recording finished!")
    return recording, sample_rate

def main():
    SAMPLE_RATE = 16000
    DURATION = 8

    choice = get_choice()
    
    if "chat" not in st.session_state or st.session_state.chat is None:
        initialize_gemini_chat()

    if st.session_state.chat is None:
        return

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if choice=="Converse with Gemini 2.5":
        if prompt := st.chat_input("Type your message here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            process_prompt(prompt)

    if choice=="Chat with an image":
        uploaded_file = st.sidebar.file_uploader("Upload an image (optional)", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            st.session_state.current_uploaded_image = uploaded_file
            st.sidebar.image(uploaded_file, caption="Current Uploaded Image", use_container_width=True)
            st.sidebar.info("Image uploaded. Your next message will include this image.")
            if prompt := st.chat_input("Type your message here..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
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
                    
                    process_prompt(f"PDF Content:\n{pdf_text}\n\nUser Question: {prompt}")
    
    if choice == "Chat with Voice":
        st.sidebar.header("🎙️ Voice Input")

        if st.sidebar.button(f"Start Recording ({DURATION}s)", key="start_record"):
            with st.spinner(f"Recording for {DURATION} seconds..."):
                audio_data, sr = record_audio(duration=DURATION, sample_rate=SAMPLE_RATE)
            
            st.audio(audio_data.tobytes(), format='audio/wav', sample_rate=sr)

            user_text = transcribe_audio(audio_data, sr)
            
            if user_text.strip():
                user_content = f"🎧 {user_text}"
                st.session_state.messages.append({"role": "user", "content": user_content})
                with st.chat_message("user"):
                    st.markdown(user_content)
                
                process_prompt(user_text)
                
if __name__ == '__main__':
    main()
