import streamlit as st
import cv2
import mediapipe as mp
import numpy as np

# MediaPipe Setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    return 360-angle if angle > 180.0 else angle

st.set_page_config(page_title="FitRise Exercise Room")

# Check if the alarm was triggered via the URL
if st.query_params.get("alarm") == "active":
    st.title("🏃 ALARM ACTIVE: 10 Squats to Stop!")
    
    if 'count' not in st.session_state: st.session_state.count = 0
    if 'stage' not in st.session_state: st.session_state.stage = "up"

    img_placeholder = st.empty()
    cap = cv2.VideoCapture(0)

    while st.session_state.count < 10:
        success, image = cap.read()
        if not success: break

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        if results.pose_landmarks:
            lmk = results.pose_landmarks.landmark
            # Hip (24), Knee (26), Ankle (28)
            h = [lmk[24].x, lmk[24].y]; k = [lmk[26].x, lmk[26].y]; a = [lmk[28].x, lmk[28].y]
            angle = calculate_angle(h, k, a)

            if angle < 90: st.session_state.stage = "down"
            if angle > 160 and st.session_state.stage == "down":
                st.session_state.stage = "up"
                st.session_state.count += 1

        img_placeholder.image(image, channels="RGB")
        st.header(f"Reps: {st.session_state.count} / 10")

    if st.session_state.count >= 10:
        st.success("Alarm Deactivated! You are officially awake.")
        st.balloons()
else:
    st.title("FitRise Standby")
    st.write("Waiting for alarm trigger from the main app...")
    streamlit
mediapipe
opencv-python-headless
numpy
