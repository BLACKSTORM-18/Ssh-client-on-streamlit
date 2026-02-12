import streamlit as st
import subprocess
import os

st.set_page_config(page_title="VOID_TERMINAL", page_icon="📟", layout="wide")

# --- 1. THE INCEPTION SETUP (Alpine Root) ---
@st.cache_resource
def setup_alpine():
    if not os.path.exists("./alpine"):
        os.makedirs("./alpine")
        # Download lite rootfs
        subprocess.run(["wget", "https://dl-cdn.alpinelinux.org/alpine/v3.18/releases/x86_64/alpine-minirootfs-3.18.4-x86_64.tar.gz"], check=True)
        subprocess.run(["tar", "-xzf", "alpine-minirootfs-3.18.4-x86_64.tar.gz", "-C", "./alpine"], check=True)
    return True

setup_alpine()

# --- 2. TERMINAL INTERFACE ---
st.title("📟 VOID@CLOUD_CONSOLE")
st.caption("Running Alpine Linux (Proot) | Root Access: Enabled")

if "history" not in st.session_state:
    st.session_state.history = "Welcome to Void Inception. Type 'help' for info.\n"

# The Terminal Display
st.text_area("Console Output", value=st.session_state.history, height=400, disabled=True)

# The Command Input
cmd = st.text_input("root@void:~#", key="cmd_input")

if st.button("Run") or (cmd and cmd != ""):
    if cmd.lower() == "clear":
        st.session_state.history = ""
    else:
        # Wrap the command in PROOT to execute inside your 'Guest' Alpine Root
        # -0 fakes the root user
        full_cmd = f"proot -0 -r ./alpine -b /dev -b /sys -b /proc {cmd}"
        
        try:
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=10)
            output = result.stdout if result.stdout else result.stderr
            st.session_state.history += f"\nroot@void:~# {cmd}\n{output}"
        except Exception as e:
            st.session_state.history += f"\nroot@void:~# {cmd}\nError: {str(e)}"
    
    # Auto-scroll/Refresh logic
    st.rerun()

# --- 3. BACKGROUND PERSISTENCE ---
st.markdown("---")
st.info("💡 Tip: To run your bot continuously, use: 'nohup python3 bot.py &' inside the command line.")
