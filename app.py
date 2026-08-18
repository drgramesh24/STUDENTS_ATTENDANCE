import streamlit as st
import cv2
import numpy as np
import os
import pandas as pd
from core_logic import register_student, verify_student, EXCEL_FILE

st.set_page_config(page_title="Smart Attendance System", page_icon="🎓", layout="wide")
st.title("🎓 Multi-Pose Smart Attendance System")

menu = ["Registration", "Verification", "View Excel Database"]
choice = st.sidebar.selectbox("Select Module", menu)

if choice == "Registration":
    st.subheader("Register New Student (Multi-Pose Capture)")
    
    col1, col2 = st.columns(2)
    with col1:
        student_id = st.text_input("Student ID")
        student_name = st.text_input("Student Name")
    with col2:
        branch = st.selectbox("Branch", ["CSE", "ECE", "EEE", "Mechanical", "Civil", "IT", "AI & ML"])
        section = st.text_input("Section (e.g., A, B, C)")

    st.write("---")
    st.markdown("### Capture Facial Poses")
    st.info("Take 6 photos covering different angles to improve detection accuracy.")

    poses = ["Closed Mouth (Front)", "Smiling (Front)", "Facing Left", "Facing Right", "Facing Up", "Facing Down"]
    captured_images = {}

    tabs = st.tabs(poses)
    for index, pose in enumerate(poses):
        with tabs[index]:
            img_buffer = st.camera_input(f"Capture: {pose}", key=f"cam_{index}")
            if img_buffer is not None:
                bytes_data = img_buffer.getvalue()
                cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                captured_images[pose] = cv2_img

    st.write("---")
    if st.button("Complete Registration & Save to Excel", type="primary"):
        if not (student_id and student_name and branch and section):
            st.warning("Please fill in Student ID, Name, Branch, and Section.")
        elif len(captured_images) == 0:
            st.warning("Please capture at least one photo pose before submitting.")
        else:
            with st.spinner("Processing facial encodings and saving record..."):
                success, message = register_student(student_id, student_name, branch, section, captured_images)
                if success:
                    st.success(message)
                else:
                    st.error(message)

elif choice == "Verification":
    st.subheader("Daily Attendance Scanner")
    img_buffer = st.camera_input("Scan face to verify identity")
    
    if img_buffer is not None:
        bytes_data = img_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        with st.spinner("Verifying identity..."):
            match_found, student_info = verify_student(cv2_img)
            if match_found:
                st.success(f"✅ Verified: {student_info}")
            else:
                st.error(f"❌ {student_info}")

elif choice == "View Excel Database":
    st.subheader("Registered Students Database (Excel)")
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        st.dataframe(df, use_container_width=True)
        
        with open(EXCEL_FILE, "rb") as file:
            st.download_button(
                label="📥 Download Excel File",
                data=file,
                file_name="students_database.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("No records found yet. Register students to auto-generate the Excel spreadsheet.")
