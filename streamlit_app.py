import streamlit as st
import subprocess
import os
import time
import requests

st.set_page_config(page_title="VOID_NGROK_POWER", page_icon="⚡")

# --- 1. THE GATEKEEPER ---
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if not st.session_state.unlocked:
    st.title("🔐 ROOT GATEWAY")
    if "auth" not in st.secrets:
        st.error("MISSING SECRETS: Add [auth] password and ngrok_token to Streamlit Settings.")
        st.stop()
    
    pwd = st.text_input("Enter Root Key:", type="password")
    if st.button("Initialize"):
        if pwd == st.secrets["auth"]["password"]:
            st.session_state.unlocked = True
            st.rerun()
    st.stop()

# --- 2. THE ENGINE ---
@st.cache_resource
def start_root_ssh():
    # Setup Ngrok properly
    if not os.path.exists("./ngrok"):
        st.toast("📥 Downloading Ngrok...", icon="🚀")
        # Download the Linux 64-bit version
        subprocess.run(["wget", "https://bin.equinox.io/c/b34239N4Z76/ngrok-v3-stable-linux-amd64.tgz"], check=True)
        subprocess.run(["tar", "-xvzf", "ngrok-v3-stable-linux-amd64.tgz"], check=True)
        subprocess.run(["chmod", "+x", "./ngrok"], check=True)
    
    # Configure token
    token = st.secrets["auth"]["ngrok_token"]
    subprocess.run(["./ngrok", "config", "add-authtoken", token], check=True)

    # Setup real SSH Server
    # We set root password to 'void123'
    subprocess.run(["mkdir", "-p", "/var/run/sshd"])
    subprocess.run("echo 'root:void123' | chpasswd", shell=True)
    
    # Start SSH daemon
    subprocess.Popen(["/usr/sbin/sshd", "-D"], close_fds=True)
    
    # Start Ngrok Tunnel
    subprocess.Popen(["./ngrok", "tcp", "22"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    
    return True

start_root_ssh()

# --- 3. THE DASHBOARD ---
st.title("⚡ VOID@UBUNTU_ROOT")

try:
    time.sleep(3) # Give Ngrok a moment to breathe
    res = requests.get("http://localhost:4040/api/tunnels").json()
    public_url = res['tunnels'][0]['public_url'] # tcp://0.tcp.ngrok.io:12345
    
    # Extract for Termius
    raw_address = public_url.replace("tcp://", "")
    address = raw_address.split(":")[0]
    port = raw_address.split(":")[1]
    
    st.success("🛰️ CLOUD TUNNEL ACTIVE")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### 🏠 Hostname")
        st.code(address, language="text")
        st.write("### 👤 Username")
        st.code("root", language="text")
    
    with col2:
        st.write("### 🔌 Port")
        st.code(port, language="text")
        st.write("### 🔑 Password")
        st.code("void123", language="text")

except:
    st.info("⌛ Cooking the tunnel... Refresh in 10s.")

st.markdown("---")
if st.button("🔥 Factory Reset Server"):
    st.cache_resource.clear()
    subprocess.run(["pkill", "-9", "ngrok"])
    st.rerun()
