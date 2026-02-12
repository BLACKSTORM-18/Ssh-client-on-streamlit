import streamlit as st
import subprocess
import os
import time
import re

st.set_page_config(page_title="Void High-Power Cloud", page_icon="💀", layout="wide")

# --- 1. THE GATEKEEPER ---
def check_auth():
    if "auth_ok" not in st.session_state:
        st.session_state.auth_ok = False
    if not st.session_state.auth_ok:
        st.title("🔒 Restricted Access")
        if "auth" not in st.secrets:
            st.error("CRITICAL: Add [auth] password='...' to Streamlit Secrets!")
            st.stop()
        pwd = st.text_input("Server Key:", type="password")
        if st.button("Access Terminal"):
            if pwd == st.secrets["auth"]["password"]:
                st.session_state.auth_ok = True
                st.rerun()
        st.stop()

check_auth()

# --- 2. THE POWER-HOUSE ENGINE ---
@st.cache_resource
def launch_full_server():
    with st.status("🏗️ Booting Full Ubuntu Environment...", expanded=True) as status:
        # Cleanup old sessions
        try:
            subprocess.run(["pkill", "-9", "tmate"], stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-9", "cloudflared"], stderr=subprocess.DEVNULL)
        except: pass
        
        st.write("✅ System Cleanup Complete.")
        
        # Launch Tmate (SSH)
        try:
            subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d"])
            st.write("✅ SSH Tunnel Initialized.")
        except FileNotFoundError:
            st.error("FATAL: 'tmate' package not found. Check packages.txt!")
            st.stop()
            
        # Download Cloudflare (IPTV/Web)
        if not os.path.exists("./cloudflared"):
            st.write("📥 Fetching Cloudflare Quick-Tunnel binary...")
            subprocess.run(["wget", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-O", "./cloudflared"])
            subprocess.run(["chmod", "+x", "./cloudflared"])
        
        with open("/tmp/cf.log", "w") as log:
            subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://localhost:8080"], stdout=log, stderr=log)
        st.write("✅ Web Tunnel (Port 8080) online.")
        
        time.sleep(7) # Extra time for the cloud to register the links
        status.update(label="🚀 Server Fully Operational", state="complete", expanded=False)
    return True

launch_full_server()

# --- 3. THE COMMAND CENTER ---
st.title("💀 VOID_ROOT@CLOUD")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.header("⚡ SSH Access")
    try:
        ssh_link = subprocess.check_output(["tmate", "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"]).decode("utf-8").strip()
        st.code(ssh_link, language="bash")
        st.caption("Paste into Termius Hostname box. Username is the text before '@'.")
    except:
        st.warning("SSH link generating... Refresh shortly.")

with col2:
    st.header("📺 IPTV Public URL")
    if os.path.exists("/tmp/cf.log"):
        with open("/tmp/cf.log", "r") as f:
            links = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", f.read())
            if links:
                st.success(links[-1])
                st.caption("Port 8080 is automatically mapped to this URL.")
            else:
                st.info("Waiting for Cloudflare link...")

st.markdown("---")
if st.button("🔄 Force Reboot Services"):
    st.cache_resource.clear()
    st.rerun()
