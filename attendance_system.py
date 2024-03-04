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

EMAIL_ADDRESS = "almaztakele433@gmail.com"
APP_PASSWORD = "jkei ouvc zogu xhqi" 

def send_email(subject, body, to_email):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    print(f"Sending email to: {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, APP_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
    print("Email sent successfully.")

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

def read_parent_emails(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    parent_emails = {}
    for line in lines:
        line_parts = line.split(':')
        if len(line_parts) >= 2:
            student = line_parts[0].strip()
            parent_email = line_parts[1].strip()
            parent_emails[student] = parent_email

    return parent_emails

def notify_teachers(present_students, absent_students, teacher_email):
    message = f"Attendance Summary:\n\nPresent Students: {', '.join(present_students)}\nAbsent Students: {', '.join(absent_students)}"
    send_email("Attendance Summary", message, teacher_email)

def main():
    with open("students_list.txt", "r") as file:
        students = file.read().splitlines()

    parent_emails = read_parent_emails("students_details.txt")  
    teacher_email = "teacher@example.com"  
    attendance_df = pd.DataFrame(index=students)

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

       
        if frame is not None:
            decoded_objects = decode(frame)
            
            for obj in decoded_objects:
                qr_data = obj.data.decode("utf-8")

                
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

        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    
    for student in students:
        if student not in last_attendance_time or can_mark_attendance(student):
            absent_students.append(student)

    print("Present Students:")
    print(present_students)
    print("Absent Students:")
    print(absent_students)

    with open("absent_students.txt", "w") as absent_file:
        absent_file.write("\n".join(absent_students))

    for student, parent_email in parent_emails.items():
        if student in present_students:
            message = f"Your child {student} is present."
        else:
            message = f"Your child {student} is absent."

        send_email("Attendance Notification", message, parent_email)

    notify_teachers(present_students, absent_students, teacher_email)

    attendance_df.to_excel("attendance.xlsx")


    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
