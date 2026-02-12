import streamlit as st
import subprocess
import os
import time

st.set_page_config(page_title="VOID_USER_OS", page_icon="👤")

# --- 1. SIMPLE AUTH ---
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if not st.session_state.unlocked:
    st.title("👤 USER GATEWAY")
    if "auth" not in st.secrets:
        st.error("MISSING SECRETS: Add [auth] password in Streamlit Settings.")
        st.stop()
    
    pwd = st.text_input("Enter Access Key:", type="password")
    if st.button("Unlock"):
        if pwd == st.secrets["auth"]["password"]:
            st.session_state.unlocked = True
            st.rerun()
    st.stop()

# --- 2. THE NON-ROOT ENGINE ---
@st.cache_resource
def start_user_ssh():
    # We check if tmate is already running to avoid the 'Handshake' error
    check = subprocess.run(["pgrep", "-x", "tmate"], capture_output=True)
    
    if check.returncode != 0:
        # Start tmate in read-write mode for the current user
        # We don't use 'sudo' or touch /etc/
        subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d"], close_fds=True)
        time.sleep(5)
        # Wait for the cloud to assign an internet link
        subprocess.run(["tmate", "-S", "/tmp/tmate.sock", "wait-for-connection"], timeout=10)
    
    return True

start_user_ssh()

# --- 3. THE DASHBOARD ---
st.title("👤 VOID@STREAMLIT_USER")

try:
    # Fetch the SSH link
    ssh_cmd = subprocess.check_output(["tmate", "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"], timeout=5).decode("utf-8").strip()
    
    # Split the link so you don't mess up Termius
    parts = ssh_cmd.split("@")
    user_token = parts[0].replace("ssh ", "")
    host_addr = parts[1]
    
    st.success("✅ CLOUD USER SESSION ACTIVE")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### 🏠 Hostname (Address)")
        st.code(host_addr, language="text")
    with col2:
        st.write("### 🔑 Username (Token)")
        st.code(user_token, language="text")
        
    st.info("In Termius: Use the Address and Username above. LEAVE PASSWORD BLANK.")

except Exception as e:
    st.warning("⌛ Server Warming Up... Refresh in 10s.")

st.markdown("---")
st.caption("Status: Non-Root Environment | Disk: Ephemeral | User: adminuser")

if st.button("🔄 Reset User Session"):
    st.cache_resource.clear()
    subprocess.run(["pkill", "-9", "tmate"])
    st.rerun()
