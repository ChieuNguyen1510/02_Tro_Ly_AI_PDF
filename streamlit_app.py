import streamlit as st
from openai import OpenAI
from base64 import b64encode
import fitz  # PyMuPDF
import os
import shutil
from tempfile import NamedTemporaryFile
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# ========== CÀI ĐẶT GOOGLE DRIVE ==========
gauth = GoogleAuth()
gauth.LoadClientConfigFile('client_secrets.json')
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)
FOLDER_ID = st.secrets["DRIVE_FOLDER_ID"]

# ========== UI ẨN TOOLBAR & CSS CHAT ==========
st.markdown("""
<style>
[data-testid="stToolbar"], [data-testid="manage-app-button"] {
    display: none !important;
}
.message {
    padding: 12px !important;
    border-radius: 12px !important;
    max-width: 75% !important;
    display: flex !important;
    align-items: flex-start !important;
    gap: 12px !important;
    margin: 8px 0 !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}
.assistant {
    background-color: #f0f7ff !important;
}
.user {
    background-color: #e6ffe6 !important;
    text-align: right !important;
    margin-left: auto !important;
    flex-direction: row-reverse !important;
}
.icon {
    width: 32px !important;
    height: 32px !important;
    border-radius: 50% !important;
    border: 1px solid #ddd !important;
}
.text {
    flex: 1 !important;
    font-size: 16px !important;
    line-height: 1.4 !important;
}
.typing {
    font-style: italic !important;
    color: #888 !important;
    padding: 5px 10px !important;
    display: flex !important;
    align-items: center !important;
}
@keyframes blink {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}
.typing::after {
    content: "..." !important;
    animation: blink 1s infinite !important;
}
[data-testid="stChatInput"] {
    border: 2px solid #ddd !important;
    border-radius: 8px !important;
    padding: 8px !important;
    background-color: #fafafa !important;
}
div.stButton > button {
    background-color: #4CAF50 !important;
    color: white !important;
    border-radius: 2px solid #FFFFFF !important;
    padding: 6px 6px !important;
    font-size: 14px !important;
    border: none !important;
    display: block !important;
    margin: 10px 0px !important;
}
div.stButton > button:hover {
    background-color: #45a049 !important;
}
</style>
""", unsafe_allow_html=True)

# ========== HÀM HỖ TRỢ ==========
def rfile(name_file):
    with open(name_file, "r", encoding="utf-8") as file:
        return file.read()

def img_to_base64(img_path):
    with open(img_path, "rb") as f:
        return b64encode(f.read()).decode()

def extract_text_from_pdf_path(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# ========== ICON ==========
assistant_icon = img_to_base64("assistant_icon.png")
user_icon = img_to_base64("user_icon.png")

# ========== LOGO ==========
try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)
except:
    pass

# ========== TIÊU ĐỀ ==========
title_content = rfile("00.xinchao.txt")
st.markdown(f"""<h1 style="text-align: center; font-size: 24px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px;">{title_content}</h1>""", unsafe_allow_html=True)

# ========== API OPENAI ==========
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if not openai_api_key:
    st.error("❌ Thiếu OPENAI_API_KEY trong secrets.toml")
    st.stop()
client = OpenAI(api_key=openai_api_key)

# ========== UPLOAD FILE PDF VÀO GOOGLE DRIVE ==========
uploaded_file = st.file_uploader("📤 Chọn file PDF để upload lên Google Drive", type=["pdf"])
if uploaded_file:
    with NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
        tf.write(uploaded_file.getbuffer())
        gfile = drive.CreateFile({'parents': [{'id': FOLDER_ID}], 'title': uploaded_file.name})
        gfile.SetContentFile(tf.name)
        gfile.Upload()
    st.success(f"✅ Đã upload: {uploaded_file.name}")

# ========== DANH SÁCH FILE PDF TỪ GOOGLE DRIVE ==========
file_list = drive.ListFile({
    'q': f"'{FOLDER_ID}' in parents and trashed=false"
}).GetList()
pdf_files = {f['title']: f for f in file_list if f['title'].endswith(".pdf")}

if not pdf_files:
    st.warning("⚠️ Thư mục Drive chưa có file PDF.")
    st.stop()

selected_pdf_name = st.selectbox("📄 Chọn file PDF từ Google Drive:", list(pdf_files.keys()))
selected_file = pdf_files[selected_pdf_name]

# ========== TẢI FILE VỀ VÀ ĐỌC ==========
selected_file.GetContentFile(selected_pdf_name)
pdf_context = extract_text_from_pdf_path(selected_pdf_name)

<<<<<<< HEAD
# Đọc nội dung system từ txt
base_system = rfile("01.system_trainning.txt")

# Reset khi chọn file khác
if "last_selected_pdf" not in st.session_state:
    st.session_state.last_selected_pdf = selected_pdf

if selected_pdf != st.session_state.last_selected_pdf:
    INITIAL_SYSTEM_MESSAGE = {
        "role": "system",
        "content": f"{base_system}\n\nTài liệu tham khảo từ PDF1:\n{pdf_context[:8000]}"
    }
    INITIAL_ASSISTANT_MESSAGE = {
        "role": "assistant",
        "content": rfile("02.assistant.txt")
    }

    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]
    st.session_state.last_selected_pdf = selected_pdf
    st.rerun()







# ======= SYSTEM MESSAGE BAN ĐẦU =======
# =======
# ========== TẠO SYSTEM MESSAGE ==========
# >>>>>>> parent of 7285b32 (a)
base_system = rfile("01.system_trainning.txt")
INITIAL_SYSTEM_MESSAGE = {
    "role": "system",
    "content": f"{base_system}\n\nTài liệu tham khảo từ PDF:\n{pdf_context[:8000]}"
}
INITIAL_ASSISTANT_MESSAGE = {
    "role": "assistant",
    "content": rfile("02.assistant.txt")
}

# ========== SESSION ==========
if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

if st.button("New chat"):
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]
    st.rerun()

# ========== HIỂN THỊ LỊCH SỬ ==========
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.markdown(f'''
        <div class="message assistant">
            <img src="data:image/png;base64,{assistant_icon}" class="icon" />
            <div class="text">{message["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)
    elif message["role"] == "user":
        st.markdown(f'''
        <div class="message user">
            <img src="data:image/png;base64,{user_icon}" class="icon" />
            <div class="text">{message["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)

# ========== CHAT INPUT ==========
if prompt := st.chat_input("Enter your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    st.markdown(f'''
    <div class="message user">
        <img src="data:image/png;base64,{user_icon}" class="icon" />
        <div class="text">{prompt}</div>
    </div>
    ''', unsafe_allow_html=True)

    typing_placeholder = st.empty()
    typing_placeholder.markdown('<div class="typing">Assistant is typing..</div>', unsafe_allow_html=True)

    response = ""
    stream = client.chat.completions.create(
        model=rfile("module_chatgpt.txt").strip(),
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        stream=True,
    )

    for chunk in stream:
        if chunk.choices:
            response += chunk.choices[0].delta.content or ""

    typing_placeholder.empty()

    st.markdown(f'''
    <div class="message assistant">
        <img src="data:image/png;base64,{assistant_icon}" class="icon" />
        <div class="text">{response}</div>
    </div>
    ''', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})
