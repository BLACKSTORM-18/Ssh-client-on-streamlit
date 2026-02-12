import streamlit as st
import subprocess
import os
import time

st.set_page_config(page_title="VOID_INCEPTION_ROOT", page_icon="🌀")

# --- 1. THE GATEKEEPER ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    pwd = st.text_input("Enter Root Key:", type="password")
    if st.button("Initialize Inception"):
        if pwd == st.secrets["auth"]["password"]:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 2. THE INCEPTION ENGINE ---
@st.cache_resource
def start_inception():
    # 1. Download Alpine Linux RootFS (Super lite, super fast)
    if not os.path.exists("./alpine"):
        os.makedirs("./alpine")
        subprocess.run(["wget", "https://dl-cdn.alpinelinux.org/alpine/v3.18/releases/x86_64/alpine-minirootfs-3.18.4-x86_64.tar.gz"], check=True)
        subprocess.run(["tar", "-xzf", "alpine-minirootfs-3.18.4-x86_64.tar.gz", "-C", "./alpine"], check=True)

    # 2. Check if Tmate is running
    check = subprocess.run(["pgrep", "-x", "tmate"], capture_output=True)
    
    if check.returncode != 0:
        # Launch Tmate and tell it to run PROOT immediately
        # This drops you DIRECTLY into the Alpine Root shell
        proot_cmd = "proot -0 -r ./alpine -b /dev -b /sys -b /proc /bin/sh"
        subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d", proot_cmd], close_fds=True)
        time.sleep(5)
        subprocess.run(["tmate", "-S", "/tmp/tmate.sock", "wait-for-connection"], timeout=10)
    
    return True

start_inception()

# --- 3. DASHBOARD ---
st.title("🌀 VOID@INCEPTION_ROOT")
st.success("✅ GUEST OS IS LIVE")

try:
    ssh_cmd = subprocess.check_output(["tmate", "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"], timeout=5).decode("utf-8").strip()
    st.code(ssh_cmd, language="bash")
    st.info("In Termius: Connect as usual. You will land in a ROOT '#' shell.")
except:
    st.warning("⌛ Building Inception... Refresh in 10s.")

st.markdown("---")
st.caption("OS: Alpine Linux (via Proot) | User: root | Mode: Zero-Permission Root")
