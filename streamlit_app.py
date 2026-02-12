import streamlit as st
import subprocess
import os
import time
import re

st.set_page_config(page_title="VOID_PRO_ROOT", page_icon="🔗")

# 1. THE GATEKEEPER
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    pwd = st.text_input("Root Password:", type="password")
    if st.button("Initialize Server"):
        if pwd == st.secrets["auth"]["password"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 2. THE FORCE-ACTIVE ENGINE
@st.cache_resource
def launch_server():
    # Force kill any stuck sessions that cause 'Handshake' errors
    subprocess.run(["pkill", "-9", "tmate"])
    subprocess.run(["pkill", "-9", "cloudflared"])
    
    # Launch Tmate
    subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d"])
    
    # Download Cloudflare
    if not os.path.exists("./cloudflared"):
        subprocess.run(["wget", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-O", "./cloudflared"])
        subprocess.run(["chmod", "+x", "./cloudflared"])
    
    # Start Cloudflare for IPTV
    with open("/tmp/cf.log", "w") as log:
        subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://localhost:8080"], stdout=log, stderr=log)
    
    return True

launch_server()

# 3. THE CONTROL CENTER
st.title("💀 VOID_FULL_CLOUD")

try:
    # We give it more time (15s) to generate a stable link
    ssh_cmd = subprocess.check_output(["tmate", "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"], timeout=15).decode("utf-8").strip()
    st.subheader("🚀 SSH SERVER ACTIVE")
    st.code(ssh_cmd)
    
    # --- THE KEEP-ALIVE SYSTEM ---
    # This prevents the cloud from freezing your terminal while you are in Termius
    st.write("---")
    st.write("🛰️ Server Heartbeat (Keep this tab open):")
    placeholder = st.empty()
    for i in range(100):
        placeholder.text(f"System Pulse: {time.ctime()} | Power: 100%")
        time.sleep(2) # Slowly update to keep the connection "hot"

except Exception as e:
    st.warning("Tunneling... Please hit Refresh in 10 seconds.")

if st.button("Hard Restart"):
    st.cache_resource.clear()
    st.rerun()
