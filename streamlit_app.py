import streamlit as st
import subprocess
import os
import time
import re

st.set_page_config(page_title="Void Cloud Terminal", page_icon="🌌", layout="centered")

# --- 1. THE SECRET VAULT ---
def check_auth():
    if "auth_ok" not in st.session_state:
        st.session_state.auth_ok = False

    if not st.session_state.auth_ok:
        st.title("🔐 Locked Terminal")
        
        # Check if secrets are even set up
        if "auth" not in st.secrets:
            st.error("⚠️ CRITICAL: Go to App Settings > Secrets and add [auth] password='your_pass'")
            st.stop()
            
        pwd = st.text_input("Enter Cloud Key:", type="password")
        if st.button("Unlock Server"):
            if pwd == st.secrets["auth"]["password"]:
                st.session_state.auth_ok = True
                st.rerun()
            else:
                st.error("❌ Wrong Key")
        st.stop()

check_auth()

# --- 2. THE BACKGROUND ENGINE ---
@st.cache_resource
def start_ghost_stack():
    with st.status("🛠️ Waking up Cloud Services...", expanded=True) as status:
        # Kill old broken processes
        subprocess.run(["pkill", "-9", "tmate"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-9", "cloudflared"], stderr=subprocess.DEVNULL)
        
        st.write("✅ Cleaning old sessions...")
        
        # Start Tmate (SSH)
        subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d"])
        st.write("✅ Tmate Tunnel starting...")
        
        # Start Cloudflare (IPTV)
        if not os.path.exists("./cloudflared"):
            st.write("📥 Downloading Cloudflare connector...")
            subprocess.run(["wget", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-O", "./cloudflared"])
            subprocess.run(["chmod", "+x", "./cloudflared"])
        
        st.write("✅ Cloudflare Tunnel zipping up...")
        with open("/tmp/cf.log", "w") as log:
            subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://localhost:8080"], stdout=log, stderr=log)
        
        time.sleep(5) # Essential: Wait for links to generate
        status.update(label="🚀 Cloud Active!", state="complete", expanded=False)
    return True

start_ghost_stack()

# --- 3. THE CONTROL CENTER ---
st.title("🌌 Void Cloud Portal")
st.markdown("---")

# SSH Section
try:
    ssh_cmd = subprocess.check_output(["tmate", "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"], timeout=5).decode("utf-8").strip()
    st.subheader("🔑 Termius SSH Command")
    st.code(ssh_cmd, language="bash")
    st.caption("Paste this into Termius 'Hostname' box. No password needed.")
except:
    st.warning("⌛ Generating SSH Tunnel... Hit refresh in 5 seconds.")

# IPTV Section
st.markdown("---")
if os.path.exists("/tmp/cf.log"):
    with open("/tmp/cf.log", "r") as f:
        log_data = f.read()
        links = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", log_data)
        if links:
            st.subheader("📺 IPTV Public Link (Port 8080)")
            st.success(links[-1])
            st.caption("No bandwidth limits. Use this in your IPTV player.")
        else:
            st.info("⌛ Cloudflare link is still being cooked... Wait a moment.")

if st.button("🔄 Refresh Links"):
    st.rerun()

st.sidebar.caption(f"Server Heartbeat: {time.ctime()}")
