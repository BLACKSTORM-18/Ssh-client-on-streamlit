import streamlit as st
import subprocess
import os
import time

st.set_page_config(page_title="VOID_INCEPTION", page_icon="🌀")

# --- 1. THE BRAIN (Background Logic) ---
@st.cache_resource
def launch_inception():
    # 1. Download the guest OS (Alpine)
    if not os.path.exists("./alpine"):
        os.makedirs("./alpine")
        # Download lite rootfs
        subprocess.run(["wget", "https://dl-cdn.alpinelinux.org/alpine/v3.18/releases/x86_64/alpine-minirootfs-3.18.4-x86_64.tar.gz"], check=True)
        subprocess.run(["tar", "-xzf", "alpine-minirootfs-3.18.4-x86_64.tar.gz", "-C", "./alpine"], check=True)

    # 2. Check if tmate is running
    status = subprocess.run(["pgrep", "-x", "tmate"], capture_output=True)
    if status.returncode != 0:
        # Start tmate and drop it STRAIGHT into the Alpine root shell
        # Proot -0 fakes the root user inside your guest folder
        cmd = "proot -0 -r ./alpine -b /dev -b /sys -b /proc /bin/sh"
        subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d", cmd], close_fds=True)
        time.sleep(5)
        subprocess.run(["tmate", "-S", "/tmp/tmate.sock", "wait-for-connection"], timeout=10)
    
    return True

launch_inception()

# --- 2. THE DASHBOARD ---
st.title("🌀 VOID@INCEPTION_ROOT")

try:
    # Fetch the SSH link
    ssh_output = subprocess.check_output(["tmate", "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"], timeout=5).decode("utf-8").strip()
    
    # Split the link to avoid manual mistakes
    parts = ssh_output.split("@")
    username = parts[0].replace("ssh ", "")
    hostname = parts[1]
    
    st.success("✅ GUEST ROOT SHELL ACTIVE")
    col1, col2 = st.columns(2)
    with col1:
        st.write("### 🏠 Hostname")
        st.code(hostname)
    with col2:
        st.write("### 👤 Username")
        st.code(username)
    
    st.info("In Termius: Connect to Hostname + Username. Leave Password EMPTY.")
except:
    st.warning("⌛ Building tunnel... Refresh in 10s.")

if st.button("🔥 Factory Reset"):
    st.cache_resource.clear()
    subprocess.run(["pkill", "-9", "tmate"])
    st.rerun()
