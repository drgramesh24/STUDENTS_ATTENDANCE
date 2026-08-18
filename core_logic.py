import cv2
import numpy as np

def register_student(student_id, student_name, cv2_image):
    """
    Takes the student info and their photo array, and saves them.
    """
    # YOUR CODE GOES HERE:
    # 1. Extract face encodings from 'cv2_image'
    # 2. Save the ID, Name, and Encoding to your database/CSV
    
    # Return True if successful
    return True

def verify_student(cv2_image):
    """
    Takes a photo array from the webcam and tries to find a match.
    """
    # YOUR CODE GOES HERE:
    # 1. Extract face encoding from 'cv2_image'
    # 2. Compare it against your saved encodings
    # 3. If a match is found, log the attendance
    
    # Return a boolean and the student's name/ID if found
    # Example: return True, "John Doe (ID: 101)"
    return False, "Unknown"