import streamlit as st
import json
import os
import time
import base64
from backend import chatbot


def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


st.set_page_config(
    page_title="CNCC Chatbot",
    page_icon="🌐",
    layout="wide"
)


# ✅ Load background image
bg_image = get_base64_image("background.jpg")


# ✅ Custom CSS - Dark Theme with Circuit Background
st.markdown(f"""
<style>
    /* Background image */
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        font-family: 'Segoe UI', sans-serif;
    }}

    /* Dark overlay */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.55);
        z-index: 0;
    }}

    /* Main title */
    h1 {{
        color: #00d4ff;
        font-size: 2rem;
        font-weight: 700;
    }}

    /* Caption */
    .stCaption {{
        color: #cccccc;
        font-size: 0.9rem;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.75);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem;
    }}

    [data-testid="stSidebar"] h1 {{
        color: #00d4ff;
        font-size: 1.3rem;
    }}

    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {{
        background-color: rgba(255, 255, 255, 0.08);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        font-size: 0.85rem;
        font-weight: 500;
        padding: 0.4rem 0.8rem;
        text-align: left;
        transition: all 0.2s ease;
    }}

    [data-testid="stSidebar"] .stButton > button:hover {{
        background-color: #00d4ff;
        color: #000000;
        border-color: #00d4ff;
    }}

    /* User chat bubble */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
        background-color: rgba(255, 255, 255, 0.12);
        border-radius: 15px;
        padding: 12px 16px;
        margin: 6px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}

    /* Assistant chat bubble */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
        background-color: rgba(255, 255, 255, 0.08);
        border-radius: 15px;
        padding: 12px 16px;
        margin: 6px 0;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
    }}

    /* Chat text */
    [data-testid="stChatMessage"] p {{
        font-size: 0.95rem;
        line-height: 1.6;
        color: #ffffff;
    }}

    /* Chat input */
    [data-testid="stChatInput"] {{
        border-radius: 20px;
        border: 1px solid rgba(0, 212, 255, 0.4);
        background-color: rgba(0, 0, 0, 0.6);
        font-size: 0.95rem;
        color: #ffffff;
    }}

    /* Spinner */
    .stSpinner {{
        color: #00d4ff;
    }}

    /* Divider */
    hr {{
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        margin: 0.5rem 0;
    }}
</style>
""", unsafe_allow_html=True)


st.title("cloUnet")
st.caption("Ask anything about Computer Networks or Cloud Computing")

CHAT_FILE = "chats.json"


def generate_title(text):
    words = text.split()
    title = " ".join(words[:6])
    if len(words) > 6:
        title += "..."
    return title


# Load chats
if "conversations" not in st.session_state:
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r") as f:
                st.session_state.conversations = json.load(f)
        except:
            st.session_state.conversations = {"New Chat": []}
    else:
        st.session_state.conversations = {"New Chat": []}


# Rename old chats
updated_conversations = {}
for chat_name, msgs in st.session_state.conversations.items():
    if chat_name.startswith("Chat") and len(msgs) > 0:
        first_question = msgs[0]["content"]
        new_name = generate_title(first_question)
        updated_conversations[new_name] = msgs
    else:
        updated_conversations[chat_name] = msgs
st.session_state.conversations = updated_conversations


if "current_chat" not in st.session_state:
    st.session_state.current_chat = list(st.session_state.conversations.keys())[0]


def save_chats():
    with open(CHAT_FILE, "w") as f:
        json.dump(st.session_state.conversations, f)


# Sidebar
with st.sidebar:
    st.title("💬 Chats")

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.conversations["New Chat"] = []
        st.session_state.current_chat = "New Chat"
        save_chats()
        st.rerun()

    st.divider()

    for chat_name in list(st.session_state.conversations.keys()):
        if st.button(chat_name, use_container_width=True):
            st.session_state.current_chat = chat_name
            st.rerun()

    st.divider()

    if st.button("🗑️ Delete Current Chat", use_container_width=True):
        if len(st.session_state.conversations) > 1:
            del st.session_state.conversations[st.session_state.current_chat]
            st.session_state.current_chat = list(
                st.session_state.conversations.keys())[0]
            save_chats()
            st.rerun()
        else:
            st.warning("Cannot delete the only chat.")


# Get current messages
messages = st.session_state.conversations[st.session_state.current_chat]


# Display chat history
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# Chat input
user_input = st.chat_input("cloUnet will help you .... ")

if user_input:

    if st.session_state.current_chat == "New Chat" and len(messages) == 0:
        new_title = generate_title(user_input)
        st.session_state.conversations[new_title] = messages
        del st.session_state.conversations["New Chat"]
        st.session_state.current_chat = new_title

    messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Thinking... 🤖"):
        try:
            result = chatbot.invoke({"question": user_input})
            answer = result.get("answer", "⚠️ No response received. Please try again.")
        except Exception as e:
            answer = f"❌ Error: {str(e)}"

    messages.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for word in answer.split():
            full_response += word + " "
            message_placeholder.markdown(full_response)
            time.sleep(0.015)

    save_chats()


