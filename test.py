import cv2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pyzbar.pyzbar import decode
import smtplib
from email.mime.text import MIMEText

last_attendance_time = {}
absent_students = []
present_students = []

# Email configuration (replace with your own details)
EMAIL_ADDRESS = "your_email@gmail.com"
APP_PASSWORD = "your_generated_app_password"  # Replace with the generated App Password

def send_email(subject, body, to_email):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, APP_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

def mark_attendance(student, attendance_df):
    now = datetime.now()
    today_timestamp = now.strftime("%Y-%m-%d")
    tomorrow_timestamp = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    if today_timestamp not in attendance_df.columns:
        attendance_df[today_timestamp] = ''

    if tomorrow_timestamp not in attendance_df.columns:
        attendance_df[tomorrow_timestamp] = ''

    attendance_df.at[student, today_timestamp] = f'Present {now.strftime("%H:%M:%S")}'
    print(f"{student} is marked present at {today_timestamp} {now.strftime('%H:%M:%S')}")
    present_students.append(student)

def can_mark_attendance(student):
    last_time = last_attendance_time.get(student, datetime.min)
    return datetime.now() - last_time > timedelta(hours=24)

def draw_rectangle(frame, corners):
    corners_np = np.array(corners, dtype=np.int32)
    corners_np = corners_np.reshape((1, -1, 2))
    cv2.polylines(frame, [corners_np], isClosed=True, color=(0, 255, 0), thickness=2)

def main():
    with open("students.txt", "r") as file:
        students = file.read().splitlines()

    attendance_df = pd.DataFrame(index=students)

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode("utf-8")

            # Check if the split operation produces a list with at least two elements
            qr_data_parts = qr_data.split(": ")
            if len(qr_data_parts) >= 2:
                student = qr_data_parts[1]
                corners = obj.polygon

                if can_mark_attendance(student):
                    mark_attendance(student, attendance_df)
                    last_attendance_time[student] = datetime.now()

                if len(corners) == 4:
                    draw_rectangle(frame, corners)

                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, f"Student: {student}", (10, 30), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow("QR Code Scanner", frame)

        # Break the loop when 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Send email notifications when stopping the camera
    for student in students:
        if student not in last_attendance_time or can_mark_attendance(student):
            absent_students.append(student)

    print("Present Students:")
    print(present_students)
    print("Absent Students:")
    print(absent_students)

    # Write absent students to a text file
    with open("absent_students.txt", "w") as absent_file:
        absent_file.write("\n".join(absent_students))

    # Send email notification to the teacher
    teacher_email = "teacher_email@gmail.com"  # Replace with the teacher's email
    send_email("Attendance Notification", f"Present students: {', '.join(present_students)}\nAbsent students: {', '.join(absent_students)}", teacher_email)

    # Send email notification to the student's parent
    parent_email = "parent_email@gmail.com"  # Replace with the parent's email
    send_email("Attendance Notification", f"Your child is absent: {', '.join(absent_students)}", parent_email)

    # Save the attendance data to an Excel file
    attendance_df.to_excel("attendance.xlsx")

    # Release the webcam
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
