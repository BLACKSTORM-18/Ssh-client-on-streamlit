import streamlit as st
import subprocess
import os
import time
import shutil

st.set_page_config(page_title="VOID_PERSISTENT", page_icon="♾️", layout="wide")

# --- 1. SECURITY LOCK ---
if "auth_state" not in st.session_state:
    st.session_state.auth_state = False

if not st.session_state.auth_state:
    st.title("🔒 VOID GATEWAY")
    pwd = st.text_input("Access Key:", type="password")
    if st.button("Authenticate"):
        if "auth" in st.secrets and pwd == st.secrets["auth"]["password"]:
            st.session_state.auth_state = True
            st.rerun()
        else:
            st.error("⛔ ACCESS DENIED")
    st.stop()

# --- 2. INTELLIGENT BACKGROUND MANAGER ---
@st.cache_resource
def maintain_infrastructure():
    # CHECK: Is Tmate already running?
    # We grep for 'tmate' to see if a process exists.
    # If it returns 0 (success), it means Tmate is ALIVE.
    tmate_status = subprocess.run(["pgrep", "-x", "tmate"], capture_output=True)
    
    if tmate_status.returncode == 0:
        st.toast("✅ Tmate is already running. Skipping restart.", icon="jj")
    else:
        st.toast("⚠️ Tmate down. Starting new session...", icon="⚙️")
        # ONLY start if it's not running
        subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d"], close_fds=True)
        time.sleep(3) # Give it time to register
        subprocess.run(["tmate", "-S", "/tmp/tmate.sock", "wait-for-connection"], timeout=10)

    # CHECK: Is Cloudflare running?
    cf_status = subprocess.run(["pgrep", "-f", "cloudflared tunnel"], capture_output=True)
    
    if cf_status.returncode != 0:
        if not os.path.exists("./cloudflared"):
            subprocess.run(["wget", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-O", "./cloudflared"])
            subprocess.run(["chmod", "+x", "./cloudflared"])
        
        with open("/tmp/cf.log", "w") as log:
            subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://localhost:8080"], stdout=log, stderr=log, close_fds=True)

    return True

maintain_infrastructure()

# --- 3. DASHBOARD ---
st.title("♾️ VOID PERSISTENT SERVER")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚡ SSH Connection")
    try:
        # Get the existing connection string
        ssh_cmd = subprocess.check_output(["tmate", "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"], timeout=5).decode("utf-8").strip()
        st.code(ssh_cmd, language="bash")
        st.caption("Paste the WHOLE string into Termius Hostname.")
    except:
        st.error("Tmate is initializing... Refresh in 5s.")

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
                st.info("Waiting for Cloudflare...")

st.markdown("---")
st.warning("⚠️ DANGER ZONE")
# Only use this button if the server is ACTUALLY broken
if st.button("🔥 KILL & RESTART EVERYTHING"):
    subprocess.run(["pkill", "-9", "tmate"])
    subprocess.run(["pkill", "-9", "cloudflared"])
    st.cache_resource.clear()
    st.rerun()
