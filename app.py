import streamlit as st
import cv2
import numpy as np
import pandas as pd
from core_logic import register_student, verify_student

st.set_page_config(page_title="Attendance System", page_icon="🎓")
st.title("🎓 Smart Attendance System")

# Create a sidebar menu
menu = ["Registration", "Verification"]
choice = st.sidebar.selectbox("Select Module", menu)

if choice == "Registration":
    st.subheader("Register a New Student")
    
    # Text Inputs
    student_id = st.text_input("Enter Student ID")
    student_name = st.text_input("Enter Student Name")
    
    # Camera Input
    img_buffer = st.camera_input("Take a clear picture")
    
    if st.button("Register"):
        if student_id and student_name and img_buffer is not None:
            # 1. Convert Streamlit image to OpenCV format
            bytes_data = img_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            # 2. Pass to your existing logic
            success = register_student(student_id, student_name, cv2_img)
            
            if success:
                st.success(f"Successfully registered {student_name}!")
            else:
                st.error("Registration failed. Try again.")
        else:
            st.warning("Please fill all fields and take a photo.")

elif choice == "Verification":
    st.subheader("Daily Attendance Scanner")
    
    img_buffer = st.camera_input("Scan face to mark attendance")
    
    if img_buffer is not None:
        with st.spinner("Verifying..."):
            # 1. Convert Streamlit image to OpenCV format
            bytes_data = img_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            # 2. Pass to your existing logic
            match_found, student_info = verify_student(cv2_img)
            
            if match_found:
                st.success(f"Attendance marked for: {student_info}")
            else:
                st.error("Face not recognized. Please try again.")