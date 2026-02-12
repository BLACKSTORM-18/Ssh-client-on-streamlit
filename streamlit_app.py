import streamlit as st
import subprocess
import os
import time
import re

st.set_page_config(page_title="VOID_ROOT_SERVER", page_icon="💀")

# --- 1. THE GATEKEEPER ---
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if not st.session_state.unlocked:
    st.title("🔐 ROOT GATEWAY")
    if "auth" not in st.secrets:
        st.error("MISSING SECRETS: Add [auth] password in Streamlit Settings.")
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
    # Setup real SSH Server
    subprocess.run(["mkdir", "-p", "/var/run/sshd"], check=True)
    # Set root password to 'void123'
    subprocess.run("echo 'root:void123' | chpasswd", shell=True, check=True)
    
    # Configure SSH to allow password login
    with open("/etc/ssh/sshd_config", "w") as f:
        f.write("PermitRootLogin yes\nPasswordAuthentication yes\n")
    
    # Start SSH daemon
    subprocess.Popen(["/usr/sbin/sshd", "-D"], close_fds=True)
    
    # Setup Cloudflare Tunnel
    if not os.path.exists("./cloudflared"):
        subprocess.run(["curl", "-L", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-o", "./cloudflared"], check=True)
        subprocess.run(["chmod", "+x", "./cloudflared"], check=True)
    
    # Start the Tunnel for SSH (Port 22)
    with open("/tmp/cf.log", "w") as log:
        subprocess.Popen(["./cloudflared", "tunnel", "--url", "ssh://localhost:22"], stdout=log, stderr=log, close_fds=True)
    
    return True

start_root_ssh()

# --- 3. THE DASHBOARD ---
st.title("💀 VOID@UBUNTU_ROOT")

if os.path.exists("/tmp/cf.log"):
    with open("/tmp/cf.log", "r") as f:
        log_data = f.read()
        links = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", log_data)
        if links:
            st.success("🛰️ CLOUD TUNNEL ACTIVE")
            st.write(f"**SSH Address:** `{links[-1].replace('https://', '')}`")
            st.write("**Username:** `root` | **Password:** `void123` | **Port:** `22` (default)")
            st.info("In Termius, just paste that Address into the Hostname box.")
        else:
            st.info("⌛ Tunneling... Refresh in 10s.")

st.markdown("---")
if st.button("🔥 Factory Reset Server"):
    st.cache_resource.clear()
    subprocess.run(["pkill", "-9", "cloudflared"])
    st.rerun()
