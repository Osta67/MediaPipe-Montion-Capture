import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Firebase Connection (Uses Streamlit Secrets for security)
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 2. MediaPipe Pose Setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    return 360-angle if angle > 180.0 else angle

st.title("FitRise: Squat to Wake Up!")
st.write("Complete 10 squats to deactivate the alarm.")

# 3. Squat Counter Logic
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
        # Hip, Knee, Ankle landmarks
        h = [lmk[24].x, lmk[24].y]; k = [lmk[26].x, lmk[26].y]; a = [lmk[28].x, lmk[28].y]
        angle = calculate_angle(h, k, a)

        # Count reps: Down (<90 deg) then Up (>160 deg)
        if angle < 90: st.session_state.stage = "down"
        if angle > 160 and st.session_state.stage == "down":
            st.session_state.stage = "up"
            st.session_state.count += 1

    img_placeholder.image(image, channels="RGB")
    st.info(f"Squats Completed: {st.session_state.count}/10")

# 4. Final Action: Tell Firebase the alarm is OFF
if st.session_state.count >= 10:
    db.collection("alarms").document("status").update({"isTriggered": False})
    st.success("Great job! Alarm dismissed.")
    st.balloons()
  
