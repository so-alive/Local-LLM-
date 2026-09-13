import streamlit as st
import requests 
import json

st.set_page_config(page_title = "Local AI Chatbot")

OLLAMA_URL = "http://localhost:11434/api/chat"


if "messages" not in st.session_state:
    st.session_state.messages = []

def clean_text(text: str) -> str:

    if not text:
        return text

    text = text.replace("\\n", "\n")
    text = text.replace("\\t", "\t")\

    return text

def stream_response(user_input, history):

    payload = {
        "model" : "gemma:2b",
        "messages" : history + [{"role" : "user", "content": user_input}],
        "stream" : True
    }

    response = requests.post(OLLAMA_URL, json = payload, stream = True)

    full_text = ""

    for line in response.iter_lines():
        if not line:
            continue

        try:

            decoded = line.decode("utf-8")
            data =json.loads(decoded)

            if "message" in data and "content" in data["message"]:

                chunk = clean_text(data["message"]["content"])

                full_text += chunk
                yield chunk

        except json.JSONDecodeError:
            continue

    return full_text

# UI

st.title("Local AI Chatbot")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask something...")   

if user_input:

    st.session_state.messages.append({"role":"user", "content":user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()

        response_text = ""

        for chunk in stream_response(user_input, st.session_state.messages):

            response_text += chunk
            placeholder.markdown(response_text)

        st.session_state.messages.append({
            "role": "assistant",
            "content" : response_text
        })

if st.button("Clear Chat"):
    st.session_state.messages =[]


# run venv\Scripts\activate to activate virtual environment.
# then streamlit run app.py 