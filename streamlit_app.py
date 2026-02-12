import streamlit as st
import subprocess
import os
import time

st.set_page_config(page_title="Void Cloud Terminal", layout="wide")

# --- 1. PASSWORD PROTECTION ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        st.title("🔐 Locked Terminal")
        pwd = st.text_input("Enter Access Key:", type="password")
        if st.button("Unlock"):
            # This checks if you did Step 1 correctly
            if "auth" not in st.secrets:
                st.error("❌ ERROR: You haven't set the password in Streamlit Settings yet!")
            elif pwd == st.secrets["auth"]["password"]:
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("❌ Incorrect Password")
        st.stop()

check_password()

# --- 2. START SERVICES (Tmate + Cloudflare) ---
@st.cache_resource
def start_services():
    with st.spinner("Waking up the cloud..."):
        # Start Tmate for Termius
        subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d"])
        
        # Start Cloudflare for IPTV
        if not os.path.exists("./cloudflared"):
            subprocess.run(["wget", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-O", "./cloudflared"])
            subprocess.run(["chmod", "+x", "./cloudflared"])
        
        with open("/tmp/cf.log", "w") as log:
            subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://localhost:8080"], stdout=log, stderr=log)
        time.sleep(5) # Give it a head start
    return True

start_services()

# --- 3. DASHBOARD UI ---
st.title("🌌 Void Cloud Terminal")
st.info("Connected to Ubuntu Cloud Server")

# FETCH SSH LINK
try:
    ssh_cmd = subprocess.check_output(["tmate", "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"]).decode("utf-8").strip()
    st.subheader("🔑 Termius SSH Command")
    st.code(ssh_cmd, language="bash")
except Exception as e:
    st.warning("⚠️ Tmate link is still generating. Wait 10 seconds and refresh.")

# FETCH IPTV LINK
if os.path.exists("/tmp/cf.log"):
    with open("/tmp/cf.log", "r") as f:
        log_data = f.read()
        import re
        links = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", log_data)
        if links:
            st.subheader("📺 IPTV Public Link (Port 8080)")
            st.success(links[-1])
        else:
            st.info("⌛ Generating IPTV Tunnel... Refresh in a moment.")

if st.button("🔄 Force Refresh"):
    st.rerun()
