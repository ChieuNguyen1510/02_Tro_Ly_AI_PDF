import streamlit as st
from openai import OpenAI
from base64 import b64encode
import fitz  # PyMuPDF
import os
import shutil
import html

# Ẩn thanh công cụ
st.markdown("""
<style>
    [data-testid="stToolbar"],
    [data-testid="manage-app-button"],
    [data-testid="stAppViewBlockContainer"] > div > div > div > div > div {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Thêm KaTeX để render công thức toán học
st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" integrity="sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV" crossorigin="anonymous">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js" integrity="sha384-XjKyOOlGwcjS3L5vY5EwA7zrx1ekL2ED4Cr3zR9Aeb2aL5lYZS3y7O6y0Q==" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" integrity="sha384-+VBxd3r6XgURycqtZ117nYw44OOcIax56Z4dCRWbxyPt0I+U7KLF+wdgH1kO" crossorigin="anonymous"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {
    renderMathInElement(document.body, {
        delimiters: [
            {left: "$$", right: "$$", display: true},
            {left: "$", right: "$", display: false},
            {left: "\\[", right: "\\]", display: true},
            {left: "\\(", right: "\\)", display: false}
        ],
        throwOnError: false
    });
});
</script>
<style>
.math-display {
    display: block;
    text-align: center;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ======= HÀM TIỆN ÍCH =======
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

# ======= ICON =======
assistant_icon = img_to_base64("assistant_icon.png")
user_icon = img_to_base64("user_icon.png")

# ======= HIỂN THỊ LOGO =======
try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)
except:
    pass

# ======= TIÊU ĐỀ =======
title_content = rfile("00.xinchao.txt")
st.markdown(f"""<h1 style="text-align: center; font-size: 24px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px;">{title_content}</h1>""", unsafe_allow_html=True)

# ======= API KEY =======
openai_api_key = st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# 📤 Tải file PDF từ máy và copy vào thư mục Document1
dst_folder = "Document1"
os.makedirs(dst_folder, exist_ok=True)

uploaded_file = st.file_uploader("📤 Upload PDF file", type=["pdf"])

if uploaded_file is not None:
    file_name = uploaded_file.name
    dst_path = os.path.join(dst_folder, file_name)

    with open(dst_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ Saved '{file_name}' go to Document folder.")

# ======= CHỌN FILE TỪ Document1 =======
pdf_files = [f for f in os.listdir(dst_folder) if f.endswith(".pdf")]
selected_pdf = st.selectbox("📄 Select PDF file: ", pdf_files)
pdf_context = extract_text_from_pdf_path(os.path.join("Document1", selected_pdf))

# ======= SYSTEM MESSAGE BAN ĐẦU =======
base_system = rfile("01.system_trainning.txt")
INITIAL_SYSTEM_MESSAGE = {
    "role": "system",
    "content": f"{base_system}\n\nreferent from PDF:\n{pdf_context[:8000]}"
}
INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": rfile("02.assistant.txt")}

# ======= SESSION STATE =======
if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

if st.button("New chat"):
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]
    st.rerun()

# ======= CSS GIAO DIỆN =======
st.markdown("""<style>
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
        0% { opacity: 0.3; }
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
</style>""", unsafe_allow_html=True)

# ======= HIỂN THỊ TIN NHẮN =======
for message in st.session_state.messages:
    if message["role"] in ["assistant", "user"]:
        # Thoát ký tự HTML và chuẩn hóa công thức
        content = message["content"].replace("[", "$$").replace("]", "$$")
        st.markdown(f'''
        <div class="message {message["role"]}">
            <img src="data:image/png;base64,{assistant_icon if message["role"] == "assistant" else user_icon}" class="icon" />
            <div class="text">{content}</div>
        </div>
        ''', unsafe_allow_html=True)

# ======= CHAT INPUT =======
if prompt := st.chat_input("Enter your question here..."):
    # Chuẩn hóa công thức trong input người dùng
    processed_prompt = prompt.replace("[", "$$").replace("]", "$$")
    st.session_state.messages.append({"role": "user", "content": processed_prompt})

    st.markdown(f'''
    <div class="message user">
        <img src="data:image/png;base64,{user_icon}" class="icon" />
        <div class="text">{processed_prompt}</div>
    </div>
    ''', unsafe_allow_html=True)

    typing_placeholder = st.empty()
    typing_placeholder.markdown('<div class="typing">Assistant is typing...</div>', unsafe_allow_html=True)

    # Gọi OpenAI API (streaming)
    response = ""
    stream = client.chat.completions.create(
        model=rfile("module_chatgpt.txt").strip(),
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        stream=True,
    )

    for chunk in stream:
        if chunk.choices:
            response += chunk.choices[0].delta.content or ""

    # Chuẩn hóa công thức trong phản hồi của trợ lý
    processed_response = response.replace("[", "$$").replace("]", "$$")

    typing_placeholder.empty()

    st.markdown(f'''
    <div class="message assistant">
        <img src="data:image/png;base64,{assistant_icon}" class="icon" />
        <div class="text">{processed_response}</div>
    </div>
    ''', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": processed_response})