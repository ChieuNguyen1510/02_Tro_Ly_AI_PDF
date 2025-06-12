import streamlit as st
from openai import OpenAI
from base64 import b64encode
import fitz  # PyMuPDF để đọc PDF
import os
import hashlib
import datetime
import json

# Ẩn thanh công cụ
st.markdown("""
<style>
    [data-testid="stToolbar"],
    [data-testid="manage-app-button"],
    [data-testid="stAppViewBlockContainer"] > div > div > div > div > div {
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
        content: "...";
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
        border-radius: 8px !important;
        padding: 6px 12px !important;
        font-size: 14px !important;
        border: none !important;
        display: block !important;
        margin: 10px 0 !important;
    }
    div.stButton > button:hover {
        background-color: #45a049 !important;
    }
    .history-item {
        padding: 10px !important;
        border-bottom: 1px solid #ddd !important;
        cursor: pointer !important;
    }
    .history-item:hover {
        background-color: #f5f5f5 !important;
    }
</style>
""", unsafe_allow_html=True)

# Hàm đọc file văn bản
def rfile(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"Lỗi: File {name_file} không tồn tại.")
        return ""
    except Exception as e:
        st.error(f"Lỗi khi đọc file {name_file}: {str(e)}")
        return ""

# Hàm chuyển ảnh thành base64
def img_to_base64(img_path):
    try:
        with open(img_path, "rb") as f:
            return b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"Lỗi: File ảnh {img_path} không tồn tại.")
        return ""
    except Exception as e:
        st.error(f"Lỗi khi xử lý ảnh {img_path}: {str(e)}")
        return ""

# Hàm đọc PDF từ file tải lên
def extract_text_from_pdf(uploaded_file):
    if not uploaded_file:
        return ""
    try:
        text = ""
        uploaded_file.seek(0)  # Đảm bảo con trỏ file ở đầu
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Lỗi khi đọc PDF: {str(e)}")
        return ""

# Hàm tóm tắt nội dung PDF
def summarize_pdf_content(text, client):
    if len(text) <= 8000:
        return text
    try:
        summary_prompt = f"Tóm tắt nội dung sau trong 2000 ký tự hoặc ít hơn:\n{text}"
        response = client.chat.completions.create(
            model=rfile("module_chatgpt.txt").strip(),
            messages=[{"role": "system", "content": summary_prompt}],
        ).choices[0].message.content
        st.warning("Nội dung PDF vượt quá 8000 ký tự, đã tóm tắt xuống còn 2000 ký tự.")
        return response
    except Exception as e:
        st.error(f"Lỗi khi tóm tắt PDF: {str(e)}")
        return text[:8000]

# Hàm tạo key cache từ prompt
def get_cache_key(messages):
    content = "".join(m["content"] for m in messages)
    return hashlib.md5(content.encode()).hexdigest()

# Hàm tạo hash từ file PDF
def get_pdf_hash(uploaded_file):
    if uploaded_file:
        uploaded_file.seek(0)
        return hashlib.md5(uploaded_file.read()).hexdigest()
    return ""

# Hàm lưu lịch sử vào file JSON
def save_chat_history():
    try:
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.chat_history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Lỗi khi lưu lịch sử vào file: {str(e)}")

# Hàm đọc lịch sử từ file JSON
def load_chat_history():
    try:
        if os.path.exists("chat_history.json"):
            with open("chat_history.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Lỗi khi đọc lịch sử từ file: {str(e)}")
        return []

# Icon
assistant_icon = img_to_base64("assistant_icon.png")
user_icon = img_to_base64("user_icon.png")

# Hiển thị logo
try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)
except:
    pass

# Tiêu đề
title_content = rfile("00.xinchao.txt")
if title_content:
    st.markdown(f"""<h1 style="text-align: center; font-size: 24px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px;">{title_content}</h1>""", unsafe_allow_html=True)

# API key
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if not openai_api_key:
    st.error("Lỗi: Không tìm thấy OPENAI_API_KEY trong st.secrets.")
    client = None
else:
    client = OpenAI(api_key=openai_api_key)

# Khởi tạo session_state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "response_cache" not in st.session_state:
    st.session_state.response_cache = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chat_history()
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = max([s["session_id"] for s in st.session_state.chat_history], default=-1) + 1
if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""
if "pdf_hash" not in st.session_state:
    st.session_state.pdf_hash = ""

# Tạo system message từ file txt + pdf
base_system = rfile("01.system_trainning.txt")
INITIAL_SYSTEM_MESSAGE = {
    "role": "system",
    "content": f"{base_system}\n\nTài liệu tham khảo từ PDF:\n{st.session_state.pdf_context}" if st.session_state.pdf_context else base_system
}
INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": rfile("02.assistant.txt")}

# Khởi tạo messages nếu rỗng
if not st.session_state.messages:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

# Tạo tab
tab1, tab2 = st.tabs(["Chat", "Lịch sử trò chuyện"])

with tab1:
    # Tải file PDF
    uploaded_file = st.file_uploader("Tải lên file PDF", type=["pdf"])
    if uploaded_file and client:
        new_pdf_hash = get_pdf_hash(uploaded_file)
        if new_pdf_hash != st.session_state.pdf_hash:
            pdf_text = extract_text_from_pdf(uploaded_file)
            if pdf_text:
                st.session_state.pdf_context = summarize_pdf_content(pdf_text, client)
                st.session_state.pdf_hash = new_pdf_hash
                # Cập nhật system message
                st.session_state.messages[0] = {
                    "role": "system",
                    "content": f"{base_system}\n\nTài liệu tham khảo từ PDF:\n{st.session_state.pdf_context}" if st.session_state.pdf_context else base_system
                }
                st.rerun()

    # Nút bắt đầu mới
    if st.button("New chat"):
        # Lưu phiên hiện tại vào lịch sử
        if len(st.session_state.messages) > 2:  # Chỉ lưu nếu có tin nhắn người dùng
            st.session_state.chat_history.append({
                "session_id": st.session_state.current_session_id,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "messages": st.session_state.messages.copy()
            })
            save_chat_history()
        st.session_state.current_session_id += 1
        st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]
        st.rerun()

    # Hiển thị tin nhắn
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

# Chat input (luôn ở dưới cùng)
if prompt := st.chat_input("Enter your question here..."):
    if not client:
        st.error("Không thể gửi tin nhắn: OPENAI_API_KEY không hợp lệ.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})

        st.markdown(f'''
        <div class="message user">
            <img src="data:image/png;base64,{user_icon}" class="icon" />
            <div class="text">{prompt}</div>
        </div>
        ''', unsafe_allow_html=True)

        typing_placeholder = st.empty()
        typing_placeholder.markdown('<div class="typing">Assistant is typing...</div>', unsafe_allow_html=True)

        # Kiểm tra cache
        cache_key = get_cache_key(st.session_state.messages)
        if cache_key in st.session_state.response_cache:
            response = st.session_state.response_cache[cache_key]
        else:
            # Gọi API
            response = ""
            try:
                stream = client.chat.completions.create(
                    model=rfile("module_chatgpt.txt").strip(),
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True,
                )
                for chunk in stream:
                    if chunk.choices:
                        response += chunk.choices[0].delta.content or ""
                st.session_state.response_cache[cache_key] = response
            except Exception as e:
                response = f"Lỗi khi gọi API OpenAI: {str(e)}"
                st.error(response)

        typing_placeholder.empty()

        st.markdown(f'''
        <div class="message assistant">
            <img src="data:image/png;base64,{assistant_icon}" class="icon" />
            <div class="text">{response}</div>
        </div>
        ''', unsafe_allow_html=True)

        st.session_state.messages.append({"role": "assistant", "content": response})
        save_chat_history()

with tab2:
    st.subheader("Lịch sử trò chuyện")
    if not st.session_state.chat_history:
        st.write("Chưa có lịch sử trò chuyện.")
    else:
        for session in st.session_state.chat_history:
            with st.expander(f"Phiên {session['session_id']} - {session['timestamp']}"):
                for message in session["messages"]:
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