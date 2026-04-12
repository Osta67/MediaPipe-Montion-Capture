import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Firebase Initialization
if not firebase_admin._apps:
    # On Streamlit Cloud, you will put your JSON keys in the "Secrets" setting
    cred_dict = dict(st.secrets["firebase"])
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. MediaPipe Pose Config
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    return 360-angle if angle > 180.0 else angle

st.set_page_config(page_title="FitRise Exercise Room", layout="wide")
st.title("🏃 Finish 10 Squats to Stop the Alarm!")

# 3. Session State for Rep Counting
if 'count' not in st.session_state: st.session_state.count = 0
if 'stage' not in st.session_state: st.session_state.stage = "up"

# Using a webcam placeholder
img_placeholder = st.empty()
cap = cv2.VideoCapture(0)

while st.session_state.count < 10:
    success, image = cap.read()
    if not success:
        st.warning("Please enable your camera.")
        break

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    if results.pose_landmarks:
        lmk = results.pose_landmarks.landmark
        # Landmarks: Hip (24), Knee (26), Ankle (28)
        hip = [lmk[24].x, lmk[24].y]
        knee = [lmk[26].x, lmk[26].y]
        ankle = [lmk[28].x, lmk[28].y]
        
        angle = calculate_angle(hip, knee, ankle)

        # Rep Logic
        if angle < 90:
            st.session_state.stage = "down"
        if angle > 160 and st.session_state.stage == "down":
            st.session_state.stage = "up"
            st.session_state.count += 1

    img_placeholder.image(image, channels="RGB")
    st.header(f"Progress: {st.session_state.count} / 10 Reps")

# 4. Success Completion
if st.session_state.count >= 10:
    db.collection("alarms").document("status").update({"isTriggered": False})
    st.success("Alarm Deactivated! Great start to your day.")
    st.balloons()
streamlit
mediapipe
opencv-python-headless
numpy
firebase-admin
