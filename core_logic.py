import cv2
import face_recognition
import pickle
import os
import numpy as np
import pandas as pd

DB_FILE = "student_faces.pkl"
EXCEL_FILE = "students_database.xlsx"

def load_database():
    """Loads encodings database."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

def save_database(db):
    """Saves encodings database."""
    with open(DB_FILE, 'wb') as f:
        pickle.dump(db, f)

def update_excel_database(student_id, student_name, branch, section, captured_poses_count):
    """Creates or updates the Excel sheet containing student records."""
    new_data = {
        "Student ID": [student_id],
        "Student Name": [student_name],
        "Branch": [branch],
        "Section": [section],
        "Poses Registered": [captured_poses_count]
    }
    new_df = pd.DataFrame(new_data)

    if os.path.exists(EXCEL_FILE):
        existing_df = pd.read_excel(EXCEL_FILE)
        # Remove duplicate if re-registering same student ID
        existing_df = existing_df[existing_df["Student ID"].astype(str) != str(student_id)]
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        updated_df = new_df

    updated_df.to_excel(EXCEL_FILE, index=False)

def register_student(student_id, student_name, branch, section, images_dict):
    """
    Extracts encodings from multiple pose images and exports student info to Excel.
    images_dict: {"Closed Mouth": cv2_img, "Smiling": cv2_img, ...}
    """
    valid_encodings = []
    failed_poses = []

    for pose_name, cv2_img in images_dict.items():
        if cv2_img is None:
            continue
            
        rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb_img, number_of_times_to_upsample=2)
        
        if len(locations) == 1:
            encoding = face_recognition.face_encodings(rgb_img, locations)[0]
            valid_encodings.append(encoding)
        else:
            failed_poses.append(pose_name)

    if len(valid_encodings) == 0:
        return False, "Failed to detect face in any of the provided images. Please re-take photos."

    # Save multiple encodings per student
    db = load_database()
    db[student_id] = {
        "name": student_name,
        "branch": branch,
        "section": section,
        "encodings": valid_encodings
    }
    save_database(db)

    # Save metadata to Excel file
    update_excel_database(student_id, student_name, branch, section, len(valid_encodings))

    msg = f"Successfully registered {student_name} with {len(valid_encodings)} face profiles saved to database & Excel."
    if failed_poses:
        msg += f" (Faces skipped due to low visibility: {', '.join(failed_poses)})"

    return True, msg


def verify_student(cv2_image):
    """Verifies unknown face against multi-encoding profiles."""
    rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image, number_of_times_to_upsample=2)
    
    if len(face_locations) == 0:
        return False, "No face detected in the camera frame."
    
    unknown_encoding = face_recognition.face_encodings(rgb_image, face_locations)[0]
    db = load_database()
    
    if not db:
        return False, "Database is empty. Register students first."
    
    # Flatten encodings to map back to student IDs
    flat_encodings = []
    student_map = []
    
    for sid, info in db.items():
        for enc in info["encodings"]:
            flat_encodings.append(enc)
            student_map.append(sid)
            
    if not flat_encodings:
        return False, "No valid encodings found in database."

    matches = face_recognition.compare_faces(flat_encodings, unknown_encoding, tolerance=0.55)
    face_distances = face_recognition.face_distance(flat_encodings, unknown_encoding)
    
    best_match_index = np.argmin(face_distances)
    
    if matches[best_match_index]:
        matched_id = student_map[best_match_index]
        s_info = db[matched_id]
        return True, f"{s_info['name']} | ID: {matched_id} | Branch: {s_info['branch']} | Sec: {s_info['section']}"
    else:
        return False, "Unknown Person"
