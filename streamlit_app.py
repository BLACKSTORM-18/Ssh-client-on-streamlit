import streamlit as st
import subprocess
import os
import time
import re

st.set_page_config(page_title="VOID_CLOUD_ROOT", page_icon="💀", layout="wide")

# --- 1. BIOMETRIC-STYLE LOCK ---
def secure_login():
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        st.title("🛡️ SECURE GATEWAY")
        if "auth" not in st.secrets:
            st.error("MISSING SECRETS: Add [auth] password='...' in Streamlit Settings.")
            st.stop()
        
        access_key = st.text_input("Enter Root Access Key:", type="password")
        if st.button("Initialize Server"):
            if access_key == st.secrets["auth"]["password"]:
                st.session_state.authorized = True
                st.rerun()
            else:
                st.error("ACCESS DENIED.")
        st.stop()

secure_login()

# --- 2. THE HEAVY-DUTY ENGINE ---
@st.cache_resource
def boot_system():
    # Kill any zombie processes blocking the ports
    try:
        subprocess.run(["pkill", "-9", "tmate"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-9", "cloudflared"], stderr=subprocess.DEVNULL)
    except: pass
    
    # Start Tmate (The SSH Bridge)
    # This creates a persistent socket for Termius to grab
    subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d"])
    
    # Setup Cloudflare (The Web/IPTV Bridge)
    if not os.path.exists("./cloudflared"):
        subprocess.run(["wget", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-O", "./cloudflared"])
        subprocess.run(["chmod", "+x", "./cloudflared"])
    
    # Map port 8080 for your IPTV/Web services
    with open("/tmp/cf.log", "w") as log:
        subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://localhost:8080"], stdout=log, stderr=log)
    
    return True

boot_system()

# --- 3. THE ROOT DASHBOARD ---
st.title("💀 VOID@CLOUD_SERVER")
st.markdown("---")

# SSH Terminal Details
try:
    # We use a 10s timeout to ensure the tunnel is fully ready before showing the link
    ssh_string = subprocess.check_output(["tmate", "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"], timeout=15).decode("utf-8").strip()
    st.header("⚡ SSH Root Access")
    st.code(ssh_string, language="bash")
    st.info("Paste the WHOLE line above into the Hostname box in Termius.")
except:
    st.warning("🔄 System Initializing... Please refresh in 10 seconds.")

# IPTV/Web Details
st.markdown("---")
if os.path.exists("/tmp/cf.log"):
    with open("/tmp/cf.log", "r") as f:
        log_txt = f.read()
        cf_links = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", log_txt)
        if cf_links:
            st.header("📺 Public Web Entry (Port 8080)")
            st.success(cf_links[-1])
            st.caption("Unlimited bandwidth IPTV/Web tunnel is live.")

if st.button("🔥 Hard Reset All Systems"):
    st.cache_resource.clear()
    st.rerun()
