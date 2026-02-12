import streamlit as st
import subprocess
import os
import time

st.set_page_config(page_title="VOID_INFINITE", page_icon="♾️")

# --- 1. THE PERSISTENT WORKER ---
@st.cache_resource
def start_persistent_root():
    # Setup Alpine/Proot if missing
    if not os.path.exists("./alpine"):
        os.makedirs("./alpine")
        subprocess.run(["wget", "https://dl-cdn.alpinelinux.org/alpine/v3.18/releases/x86_64/alpine-minirootfs-3.18.4-x86_64.tar.gz"], check=True)
        subprocess.run(["tar", "-xzf", "alpine-minirootfs-3.18.4-x86_64.tar.gz", "-C", "./alpine"], check=True)

    # Check if tmate is already running
    check = subprocess.run(["pgrep", "-x", "tmate"], capture_output=True)
    if check.returncode != 0:
        # Start tmate with Inception (Proot)
        # We use a custom socket and a long-lived session name 'void'
        cmd = "proot -0 -r ./alpine -b /dev -b /sys -b /proc /bin/sh"
        subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d", "-s", "void", cmd], close_fds=True)
        time.sleep(5)
        subprocess.run(["tmate", "-S", "/tmp/tmate.sock", "wait-for-connection"], timeout=10)
    
    return True

# Initialize the background process
start_persistent_root()

# --- 2. THE UI & KEEP-ALIVE DASHBOARD ---
st.title("♾️ VOID INFINITE ROOT")

try:
    # Fetch the SSH link
    ssh_cmd = subprocess.check_output(["tmate", "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"], timeout=5).decode("utf-8").strip()
    
    st.success("✅ PERSISTENT ROOT ACTIVE")
    
    # Split for Termius
    parts = ssh_cmd.split("@")
    user_token = parts[0].replace("ssh ", "")
    host_addr = parts[1]
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### 🏠 Hostname")
        st.code(host_addr)
    with col2:
        st.write("### 👤 Username")
        st.code(user_token)

    st.markdown("---")
    st.info("🛰️ **PERSISTENCE MODE**: Closing the tab may cause a sleep after 15-30 mins of inactivity.")
    
    # Simple UI Heartbeat to show it's working
    st.write(f"🟢 Last Pulse: {time.strftime('%H:%M:%S')}")

except Exception as e:
    st.warning("⌛ Awakening Server... If this takes >30s, click Factory Reset.")

if st.button("🔥 Factory Reset"):
    st.cache_resource.clear()
    subprocess.run(["pkill", "-9", "tmate"])
    st.rerun()
