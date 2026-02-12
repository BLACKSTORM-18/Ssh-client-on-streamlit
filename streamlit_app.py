import streamlit as st
import subprocess
import os
import time

st.set_page_config(page_title="Void Cloud Terminal", page_icon="⚡")

# --- BACKGROUND SERVICES ---
@st.cache_resource
def start_services():
    # 1. Start Tmate (SSH for Termius)
    # If you have a tmate API key, use: tmate -k YOUR_KEY -n void-cloud
    subprocess.Popen(["tmate", "-S", "/tmp/tmate.sock", "new-session", "-d"])
    
    # 2. Download and Start Cloudflare Quick Tunnel (For IPTV on 8080)
    # We download the binary manually since it's not in standard apt
    if not os.path.exists("./cloudflared"):
        subprocess.run(["wget", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-O", "./cloudflared"])
        subprocess.run(["chmod", "+x", "./cloudflared"])
    
    # Start the tunnel and log output to a file so we can read the URL
    with open("/tmp/cf.log", "w") as log:
        subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://localhost:8080"], stdout=log, stderr=log)
    
    return True

# Initialize
start_services()

# --- UI DESIGN ---
st.title("🌌 Void Cloud Terminal")
st.markdown("---")

col1, col2 = st.columns(2)

# Fetch SSH Link
try:
    ssh_link = subprocess.check_output(["tmate", "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"]).decode("utf-8").strip()
    st.subheader("🔑 Termius SSH Command")
    st.code(ssh_link, language="bash")
except:
    st.warning("Tmate is warming up... refresh in 5 seconds.")

# Fetch IPTV Link
try:
    with open("/tmp/cf.log", "r") as f:
        log_content = f.read()
        # Find the .trycloudflare.com link in the logs
        import re
        links = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", log_content)
        if links:
            st.subheader("📺 IPTV Public Link")
            st.success(links[-1])
            st.info("Run your IPTV server on port 8080 to use this link.")
except:
    st.info("Generating IPTV tunnel link...")

st.markdown("---")
if st.button("🔄 Refresh Links"):
    st.rerun()

st.caption(f"Last heartbeat: {time.ctime()}")
