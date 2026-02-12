import streamlit as st
import subprocess
import os
import time
import shutil

st.set_page_config(page_title="VOID_TERMINAL", page_icon="💀", layout="wide")

# --- 1. THE ENGINE (Logic Only, No UI) ---
@st.cache_resource
def start_server():
    # This function runs ONCE and stays alive. 
    # It does NOT touch the screen, so it won't crash.
    
    # Check if Tmate is running
    tmate_check = subprocess.run(["pgrep", "-x", "tmate"], capture_output=True)
    
    if tmate_check.returncode != 0:
        # Kill any zombies
        subprocess.run(["pkill", "-9", "tmate"])
        # Start fresh
        subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d"], close_fds=True)
        # Wait for it to connect to the internet
        subprocess.run(["tmate", "-S", "/tmp/tmate.sock", "wait-for-connection"], timeout=10)

    # Check Cloudflare
    cf_check = subprocess.run(["pgrep", "-f", "cloudflared"], capture_output=True)
    
    if cf_check.returncode != 0:
        if not os.path.exists("./cloudflared"):
            subprocess.run(["wget", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-O", "./cloudflared"])
            subprocess.run(["chmod", "+x", "./cloudflared"])
        
        with open("/tmp/cf.log", "w") as log:
            subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://localhost:8080"], stdout=log, stderr=log, close_fds=True)
            
    return True

# Start the engine
start_server()

# --- 2. THE DASHBOARD (UI Only) ---
st.title("💀 VOID ROOT SERVER")

# Get SSH Link
try:
    ssh_output = subprocess.check_output(["tmate", "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"], timeout=5).decode("utf-8").strip()
    
    # PARSE THE LINK FOR YOU
    # Example: ssh 9qtv...@sfo2.tmate.io
    parts = ssh_output.split("@")
    username = parts[0].replace("ssh ", "")
    hostname = parts[1]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Hostname (Address)")
        st.code(hostname, language="text")
    with col2:
        st.subheader("2. Username")
        st.code(username, language="text")
        
    st.info("Copy these EXACTLY into Termius. Leave Password BLANK.")

except Exception as e:
    st.error("Tmate is connecting... Hit Refresh in 5 seconds.")

st.markdown("---")

# Get Cloudflare Link
if os.path.exists("/tmp/cf.log"):
    with open("/tmp/cf.log", "r") as f:
        import re
        content = f.read()
        links = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
        if links:
            st.success(f"Web Tunnel (Port 8080): {links[-1]}")

if st.button("Reboot Server"):
    st.cache_resource.clear()
    subprocess.run(["pkill", "-9", "tmate"])
    st.rerun()
