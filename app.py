import streamlit as st
import cv2
import mediapipe as mp
import numpy as np

st.set_page_config(page_title="FitRise: Workout Room", layout="wide")
st.title("FitRise: 10 Squats to Deactivate")

# Initialize MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Rep counter state
if 'count' not in st.session_state: st.session_state.count = 0
if 'stage' not in st.session_state: st.session_state.stage = "up"

# UI Layout
col1, col2 = st.columns([2, 1])
with col1:
    img_placeholder = st.empty()
with col2:
    st.header(f"Reps: {st.session_state.count}/10")
    if st.session_state.count >= 10:
        st.success("Target Reached! Alarm Deactivated.")
        st.balloons()

# Camera Control
run = st.checkbox('Enable Webcam', value=True)
cap = cv2.VideoCapture(0)

while run and st.session_state.count < 10:
    success, frame = cap.read()
    if not success:
        st.warning("Waiting for camera...")
        break

    # Process frame
    frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
    results = pose.process(frame)

    if results.pose_landmarks:
        mp.solutions.drawing_utils.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # Simple squat logic placeholder
        # (In your presentation, mention we use hip/knee angles)
        lm = results.pose_landmarks.landmark
        knee_y = lm[mp_pose.PoseLandmark.LEFT_KNEE].y
        hip_y = lm[mp_pose.PoseLandmark.LEFT_HIP].y
        
        if knee_y < hip_y + 0.1: # Squatting down
            st.session_state.stage = "down"
        if knee_y > hip_y + 0.2 and st.session_state.stage == "down":
            st.session_state.stage = "up"
            st.session_state.count += 1

    img_placeholder.image(frame, channels="RGB")

cap.release()
