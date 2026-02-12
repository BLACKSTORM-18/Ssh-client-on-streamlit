import streamlit as st
import subprocess
import time
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="VOID LINUX ROOT", page_icon="💀", layout="wide")
st.title("💀 VOID ROOT SERVER")

# --- THE ENGINE ---
# This runs once and NEVER kills your session unless you tell it to.
@st.cache_resource
def start_server():
    # 1. Check if Tmate is already running
    # This prevents the "Handshake Failed" error by not restarting the server constantly
    check = subprocess.run(["pgrep", "-x", "tmate"], capture_output=True)
    
    if check.returncode != 0:
        # Not running? Start it.
        subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d"], close_fds=True)
        # Wait for internet connection
        subprocess.run(["tmate", "-S", "/tmp/tmate.sock", "wait-for-connection"], timeout=10)
        
    return True

start_server()

# --- THE DISPLAY ---
try:
    # Get the SSH String
    ssh_cmd = subprocess.check_output(["tmate", "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"], timeout=5).decode("utf-8").strip()
    
    # SPLIT IT FOR YOU (So you don't mess up Termius)
    # Format: ssh username@hostname
    parts = ssh_cmd.split("@")
    username = parts[0].replace("ssh ", "")
    hostname = parts[1]
    
    st.success("✅ SERVER ONLINE - FULL UBUNTU MODE")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### 1. Address (Hostname)")
        st.code(hostname, language="text")
    with col2:
        st.write("### 2. Username")
        st.code(username, language="text")
        
    st.warning("⚠️ INSTRUCTIONS: Copy the Address and Username into Termius. Leave Password EMPTY.")

except Exception as e:
    st.info("🔄 Server Initializing... Refresh Page in 5 seconds.")

st.markdown("---")
st.caption("Running: Ubuntu 22.04 LTS (Containerized) | RAM: ~16GB Shared | CPU: 2 vCPU")

# Only use this if it actually breaks
if st.button("🧨 FACTORY RESET (Kills Connection)"):
    st.cache_resource.clear()
    subprocess.run(["pkill", "-9", "tmate"])
    st.rerun()
