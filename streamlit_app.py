import streamlit as st
import subprocess
import os
import time

st.set_page_config(page_title="VOID_NGROK_CLOUD", page_icon="⚡")

# 1. AUTH CHECK
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if not st.session_state.unlocked:
    pwd = st.text_input("Enter Access Key:", type="password")
    if st.button("Unlock"):
        if pwd == st.secrets["auth"]["password"]:
            st.session_state.unlocked = True
            st.rerun()
    st.stop()

# 2. THE SSH + NGROK ENGINE
@st.cache_resource
def start_ngrok_ssh():
    # Setup Ngrok Binary
    if not os.path.exists("./ngrok"):
        subprocess.run(["wget", "https://bin.equinox.io/c/b34239N4Z76/ngrok-v3-stable-linux-amd64.tgz"], stderr=subprocess.DEVNULL)
        subprocess.run(["tar", "-xvzf", "ngrok-v3-stable-linux-amd64.tgz"], stderr=subprocess.DEVNULL)
    
    # Configure Ngrok
    token = st.secrets["auth"]["ngrok_token"]
    subprocess.run(["./ngrok", "config", "add-authtoken", token])

    # Setup SSH Server (sshd)
    # Create a user 'void' with password 'cloud'
    subprocess.run(["mkdir", "-p", "/var/run/sshd"])
    subprocess.run("echo 'root:void123' | chpasswd", shell=True)
    # Allow Root Login via SSH
    with open("/etc/ssh/sshd_config", "a") as f:
        f.write("\nPermitRootLogin yes\nPasswordAuthentication yes\n")
    
    # Start SSH service
    subprocess.Popen(["/usr/sbin/sshd", "-D"])
    
    # Start Ngrok Tunnel for Port 22
    subprocess.Popen(["./ngrok", "tcp", "22"], stdout=subprocess.DEVNULL)
    
    return True

start_ngrok_ssh()

st.title("⚡ VOID NGROK TERMINAL")

# 3. GET THE NGROK URL
try:
    # We query the local Ngrok API to find the public URL
    import requests
    time.sleep(2)
    api_url = "http://localhost:4040/api/tunnels"
    res = requests.get(api_url).json()
    public_url = res['tunnels'][0]['public_url'] # e.g. tcp://0.tcp.ngrok.io:12345
    
    # Parse for Termius
    address = public_url.replace("tcp://", "").split(":")[0]
    port = public_url.split(":")[-1]
    
    st.success("✅ SSH TUNNEL ACTIVE")
    st.write(f"**Hostname:** `{address}`")
    st.write(f"**Port:** `{port}`")
    st.write(f"**Username:** `root`")
    st.write(f"**Password:** `void123`")
    
except:
    st.info("⌛ Tunneling... If this stays for 30s, check your Ngrok Token in Secrets.")

if st.button("Restart Services"):
    st.cache_resource.clear()
    st.rerun()
