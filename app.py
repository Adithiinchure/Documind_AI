import streamlit as st
import requests
import time

# -----------------------------
# Backend URL
# -----------------------------
API_URL = "http://127.0.0.1:8000"

# -----------------------------
# Streamlit Config
# -----------------------------
st.set_page_config(page_title="DocuMind AI", page_icon="🧠", layout="wide")
st.title("🧠DocuMind AI")
st.caption("Chat with your files and URLS")

# -----------------------------
# Sidebar: Backend Connection Check
# -----------------------------
st.sidebar.header("⚙️ Backend Connection")

def check_backend(retries=3, delay=2):
    for i in range(retries):
        try:
            ping = requests.get(f"{API_URL}/docs", timeout=3)
            if ping.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            time.sleep(delay)
    return False

backend_running = check_backend()
if backend_running:
    st.sidebar.success("✅ Backend is running")
else:
    st.sidebar.error("🚫 Cannot connect to backend. Please start FastAPI first.")
    st.stop()  # Stop Streamlit until backend is ready

# -----------------------------
# Sidebar: PDF Upload Section
# -----------------------------
st.sidebar.header("📄 Upload PDFs")
uploaded_files = st.sidebar.file_uploader("Select PDFs", accept_multiple_files=True, type=["pdf"])
if uploaded_files and st.sidebar.button("🚀 Upload PDFs"):
    files = [("files", (f.name, f.getvalue(), "application/pdf")) for f in uploaded_files]
    with st.spinner("Uploading and processing PDFs..."):
        try:
            res = requests.post(f"{API_URL}/upload-files/", files=files, timeout=60)
            if res.status_code == 200:
                st.sidebar.success(res.json().get("message", "✅ PDF processed and stored!"))
            else:
                st.sidebar.error(f"❌ Error: {res.text}")
        except requests.exceptions.RequestException as e:
            st.sidebar.error(f"🚫 Connection error: {e}")

# -----------------------------
# Sidebar: URL Processing Section
# -----------------------------
st.sidebar.header("🌐 Process URLs")
urls = st.sidebar.text_area("Enter URLs (comma-separated)")
if st.sidebar.button("🔍 Process URLs"):
    url_list = [u.strip() for u in urls.split(",") if u.strip()]
    if not url_list:
        st.sidebar.warning("Please enter at least one URL.")
    else:
        with st.spinner("Fetching and processing URLs..."):
            try:
                res = requests.post(f"{API_URL}/process-urls/", json={"urls": url_list}, timeout=60)
                if res.status_code == 200:
                    st.sidebar.success(res.json().get("message", "✅ URLs processed and stored!"))
                else:
                    st.sidebar.error(f"❌ Error: {res.text}")
            except requests.exceptions.RequestException as e:
                st.sidebar.error(f"🚫 Connection error: {e}")

# -----------------------------
# Main Chat Section
# -----------------------------
st.subheader("💬 Ask a question about your data")

if "history" not in st.session_state:
    st.session_state["history"] = []

query = st.text_input("Type your question here:")
rank_type = st.selectbox("Select ranking type", ["adaptive", "corrective"], index=0)

if st.button("💡 Generate Answer"):
    if query.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                res = requests.post(
                    f"{API_URL}/generate-response/",
                    json={"query": query, "rank_type": rank_type},
                    timeout=60
                )
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "No answer found.")
                    sources = data.get("sources", [])

                    st.session_state["history"].append((query, answer))

                    st.markdown(f"### 🧾 Answer ({rank_type} ranking):")
                    st.write(answer)
                    st.caption(f"📚 Sources: {', '.join(sources)}")
                else:
                    st.error(f"❌ Server Error: {res.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"🚫 Connection error: {e}")

# -----------------------------
# Display Chat History
# -----------------------------
if st.session_state["history"]:
    st.markdown("---")
    st.subheader("🗂️ Chat History")
    for i, (q, a) in enumerate(reversed(st.session_state["history"]), 1):
        with st.expander(f"Q{i}: {q}"):
            st.write(a)
