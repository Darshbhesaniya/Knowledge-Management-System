import streamlit as st
import sys
import os
import requests

_current_dir = os.path.dirname(os.path.abspath(__file__))
_path = os.path.abspath(os.path.join(_current_dir, '..', '..', '..', 'ai_python'))

if _path not in sys.path:
    sys.path.insert(0, _path)

from rag_chat import get_rag_response


# Configuration setup
EXPRESS_API_URL = "http://localhost:5000/api/uploads"
ADMIN_PASSWORD = "admin"

# ---------------------------------------------
# 1. Page Setup
# ---------------------------------------------
st.set_page_config(page_title="KMS Chatbot", page_icon="🤖", layout="wide")

st.title("🤖 KMS Assistant")
st.caption("AI chatbot based on your company's documents and policies")
st.divider()

# =======================
# 2. Admin Panel
# =======================

# ---------------------------------------------
# 2. Sidebar: Admin Panel & Upload
# ---------------------------------------------
with st.sidebar:
    st.header("🔒 Admin Panel")
    
    # 2.1 Password Input
    entered_password = st.text_input("Enter Admin Password to upload documents", type="password")
    
    # 2.2 Check Password
    if entered_password == ADMIN_PASSWORD:
        st.success("✅ Admin Access Granted")
        st.write("Upload new policies or documents to the KMS here.")
        
        # 🆕 ADDED: accept_multiple_files
        uploaded_files = st.file_uploader("Choose documents", type=["pdf", "ppt", "pptx"], accept_multiple_files=True)
        
        if st.button("Upload to Database", type="primary"):
            if uploaded_files: # Check if the list of files is not empty
                with st.spinner(f"Uploading {len(uploaded_files)} files to Backend... ⏳"):
                    
                    # 🆕 ADDED: A loop to upload files one by one
                    for uploaded_file in uploaded_files:
                        try:
                            # Determine MIME type based on extension
                            ext = os.path.splitext(uploaded_file.name)[1].lower()
                            mime_type = "application/pdf" if ext == ".pdf" else "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                            
                            files = {"files": (uploaded_file.name, uploaded_file.getvalue(), mime_type)}
                            response = requests.post(EXPRESS_API_URL, files=files)
                            
                            if response.status_code in [200, 201]:
                                st.success(f"✅ '{uploaded_file.name}' successfully uploaded!")
                            else:
                                st.error(f"❌ Failed to upload '{uploaded_file.name}'. Server responded: {response.status_code}")
                                
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Could not connect to the backend. Is your Node.js server running?")
                            break # Stop the loop if the server is completely down
                        except Exception as e:
                            st.error(f"❌ Error with '{uploaded_file.name}': {str(e)}")
            else:
                st.warning("⚠️ Please select at least one file first before uploading.")
                
    elif entered_password != "":
        st.error("❌ Incorrect Password")
    else:
        st.info("Employees: Use the chat on the right to ask questions.")



# ---------------------------------------------
# 3. Chat History Management (Session State)
# ---------------------------------------------
# Initialize chat history if it's empty
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Initial message from the AI
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I am your AI assistant. You can ask me any question based on the uploaded documents."
    })

# Display past chat messages on the screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------
# 3. User Input and AI Response
# ---------------------------------------------
prompt = st.chat_input("Type your question here... (e.g. What is the vacation policy?)")
if prompt:

    # 3.1 Display the user's message in the UI and save it to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3.2 Fetch the AI's response
    with st.chat_message("assistant"):
        with st.spinner("AI is reading the documents... ⏳"):
            
            # Call the backend function
            response_data = get_rag_response(prompt)
            
            ans = response_data["answer"]
            sources = response_data["sources"]

            # Properly format the answer and the sources
            final_reply = f"{ans}\n\n"
            if sources:
                final_reply += "---\n**📚 Sources:**\n"
                for s in sources:
                    final_reply += f"- `{s}`\n"

            # Display the final answer in the UI
            st.markdown(final_reply)

    # 3.3 Save the AI's message to the history
    st.session_state.messages.append({"role": "assistant", "content": final_reply})

# uv run python -m streamlit run src/streamlit_ui/app.py