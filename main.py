import streamlit as st
import serial
import time
import pandas as pd

st.set_page_config(page_title="ESP32 GPS Tracker", layout="centered")

@st.cache_data(ttl=60)
def read_serial_data(port, baud, timeout):
    try:
        with serial.Serial(port, baud, timeout=timeout) as ser:
            start = time.time()
            lines = []
            while time.time() - start < 3:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    lines.append(line)
            return lines
    except Exception as e:
        return [f"Error: {e}"]

st.title("📍 ESP32 GPS Tracker Interface")

serial_port = st.sidebar.selectbox("Select Serial Port", ["/dev/ttyUSB0", "COM3", "COM4"])
baud_rate = st.sidebar.slider("Baud Rate", 4800, 115200, 9600, step=100)
poll_interval = st.sidebar.slider("Polling Interval (seconds)", 1, 60, 10)

if "gps_log" not in st.session_state:
    st.session_state.gps_log = []

if st.button("📡 Fetch GPS Data"):
    data = read_serial_data(serial_port, baud_rate, timeout=5)
    for line in data:
        if "$GPGGA" in line or "$GPRMC" in line:
            st.session_state.gps_log.append(line)
    st.success("Data Fetched")

if st.session_state.gps_log:
    st.subheader("📍 Last Known Data")
    st.code(st.session_state.gps_log[-1], language="text")

    st.subheader("🗂️ All Captured GPS Logs")
    df = pd.DataFrame({"Raw Data": st.session_state.gps_log})
    st.dataframe(df, use_container_width=True)

    if st.button("🧹 Clear Logs"):
        st.session_state.gps_log.clear()
