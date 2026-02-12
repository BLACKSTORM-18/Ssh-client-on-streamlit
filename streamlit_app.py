import streamlit as st
import subprocess
import os
import time

# 1. AUTHENTICATION CHECK
# This stops the app from showing anything unless the password is correct
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        st.title("🔐 Access Restricted")
        password = st.text_input("Enter password to unlock terminal:", type="password")
        if st.button("Unlock"):
            # Matches the password you set in the Streamlit Settings dashboard
            if password == st.secrets["auth"]["password"]:
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("❌ Wrong password. Try again.")
        st.stop() # Stops execution here if not logged in

# Run the check
check_password()

# 2. BACKGROUND SERVICES (Only starts after login)
@st.cache_resource
def start_services():
    subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d"])
    if not os.path.exists("./cloudflared"):
        subprocess.run(["wget", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-O", "./cloudflared"])
        subprocess.run(["chmod", "+x", "./cloudflared"])
    with open("/tmp/cf.log", "w") as log:
        subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://localhost:8080"], stdout=log, stderr=log)
    return True

start_services()

# 3. YOUR DASHBOARD (Now Protected)
st.title("🌌 Void Cloud Terminal")
# ... (rest of your existing UI code here) ...
