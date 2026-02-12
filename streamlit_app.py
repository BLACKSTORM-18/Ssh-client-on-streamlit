import streamlit as st
import subprocess
import os
import time
import shutil

st.set_page_config(page_title="VOID_PERSISTENT", page_icon="♾️", layout="wide")

# --- 1. SECURITY ---
if "auth_state" not in st.session_state:
    st.session_state.auth_state = False

if not st.session_state.auth_state:
    st.title("🔒 VOID GATEWAY")
    pwd = st.text_input("Access Key:", type="password")
    if st.button("Authenticate"):
        # If you haven't set secrets yet, this prevents a crash
        if "auth" in st.secrets and pwd == st.secrets["auth"]["password"]:
            st.session_state.auth_state = True
            st.rerun()
        else:
            st.error("⛔ ACCESS DENIED (Check your Secrets!)")
    st.stop()

# --- 2. BACKGROUND LOGIC (NO UI HERE!) ---
@st.cache_resource
def start_infrastructure():
    # This function ONLY handles processes. No st.toast, no st.write.
    
    # 1. Check Tmate
    # We use pgrep to see if it's already running
    tmate_check = subprocess.run(["pgrep", "-x", "tmate"], capture_output=True)
    
    if tmate_check.returncode != 0:
        # If not running, start it
        subprocess.run(["pkill", "-9", "tmate"]) # Safety kill
        subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d"], close_fds=True)
        time.sleep(2)
        subprocess.run(["tmate", "-S", "/tmp/tmate.sock", "wait-for-connection"], timeout=5)

    # 2. Check Cloudflare
    cf_check = subprocess.run(["pgrep", "-f", "cloudflared tunnel"], capture_output=True)
    
    if cf_check.returncode != 0:
        if not os.path.exists("./cloudflared"):
            subprocess.run(["wget", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-O", "./cloudflared"])
            subprocess.run(["chmod", "+x", "./cloudflared"])
        
        with open("/tmp/cf.log", "w") as log:
            subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://localhost:8080"], stdout=log, stderr=log, close_fds=True)
            
    return "Running"

# Start the background tasks
status = start_infrastructure()

# --- 3. UI DASHBOARD (UI GOES HERE) ---
st.title("♾️ VOID PERSISTENT SERVER")

# Show status quietly
if status == "Running":
    st.caption("✅ Background services active")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚡ SSH Connection")
    try:
        ssh_cmd = subprocess.check_output(["tmate", "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"], timeout=5).decode("utf-8").strip()
        st.code(ssh_cmd, language="bash")
        st.caption("Paste into Termius Hostname.")
    except:
        st.info("Generating SSH link... Refresh in 5s.")

with col2:
    st.subheader("🌐 Web Tunnel (8080)")
    if os.path.exists("/tmp/cf.log"):
        with open("/tmp/cf.log", "r") as f:
            import re
            content = f.read()
            links = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
            if links:
                st.success(links[-1])
            else:
                st.info("Waiting for Cloudflare link...")

if st.button("🔥 EMERGENCY REBOOT"):
    st.cache_resource.clear()
    subprocess.run(["pkill", "-9", "tmate"])
    subprocess.run(["pkill", "-9", "cloudflared"])
    st.rerun()
