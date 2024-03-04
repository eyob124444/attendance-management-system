import os
import pandas as pd

def is_valid_phone_number(phone_number):
    return len(phone_number) == 10 and phone_number.isdigit()

def is_valid_email(email):
    return "@" in email

def is_valid_section(section):
    return section.isalpha() and len(section) == 1

def remove_duplicates(file_path):
    lines_seen = set()

    with open(file_path, "r") as input_file:
        lines = input_file.readlines()

    with open(file_path, "w") as output_file:
        for line in lines:
            if line not in lines_seen:
                output_file.write(line)
                lines_seen.add(line)

def remove_duplicates_from_excel(file_path):
    df = pd.read_excel(file_path)
    df = df.drop_duplicates()
    df.to_excel(file_path, index=False)

def create_student_database():
    class_folder = "student_database"
    if not os.path.exists(class_folder):
        os.makedirs(class_folder)

    try:
        while True:
            class_section = input("Enter the class and section (e.g., 12a): ").lower()

            if not class_section:
                break

            student_file_path = os.path.join(class_folder, f"{class_section}.xlsx")
            students_list_file_path = "students_list.txt"
            students_details_file_path = "students_details.txt"

            student_data = {
                "Name": [],
                "Father Name": [],
                "Parent Phone Number": [],
                "Parent Email": [],
                "Class": [],
                "Section": []
            }

            if os.path.exists(student_file_path):
                student_df = pd.read_excel(student_file_path)
                student_data["Name"] = student_df["Name"].tolist()
                student_data["Father Name"] = student_df["Father Name"].tolist()
                student_data["Parent Phone Number"] = student_df["Parent Phone Number"].tolist()
                student_data["Parent Email"] = student_df["Parent Email"].tolist()
                student_data["Class"] = student_df["Class"].tolist()
                student_data["Section"] = student_df["Section"].tolist()

            while True:
                name = input("Enter student name (leave blank to finish): ")
                if not name:
                    break

                father_name = input("Enter father name: ")

                while True:
                    phone_number = input("Enter parent phone number (10 digits): ")
                    if is_valid_phone_number(phone_number):
                        break
                    else:
                        print("Invalid phone number. Please enter a 10-digit number.")

                while True:
                    email = input("Enter parent email (must contain '@'): ")
                    if is_valid_email(email):
                        break
                    else:
                        print("Invalid email address. Please include '@' in the email.")

                while True:
                    section = input("Enter section (single letter): ")
                    if is_valid_section(section):
                        break
                    else:
                        print("Invalid section. Please enter a single letter.")

                confirm = input("Press Enter to save this information (or type anything to discard): ")
                if not confirm:
                    student_data["Name"].append(name.capitalize())
                    student_data["Father Name"].append(father_name.capitalize())
                    student_data["Parent Phone Number"].append(phone_number)
                    student_data["Parent Email"].append(email)
                    student_data["Class"].append(class_section[:-1])
                    student_data["Section"].append(section)
                    print("Student information saved.")
                else:
                    print("Information discarded.")
                    break

            student_df = pd.DataFrame(student_data)
            student_df.to_excel(student_file_path, index=False)
            print(f"Student information saved for class {class_section}")

            
            with open(students_list_file_path, "a") as students_list_file:
                students_list_file.write("\n".join([f"{name} {father_name} {class_section}{section}" for name, father_name, class_section, section in zip(student_data["Name"], student_data["Father Name"], student_data["Class"], student_data["Section"])]) + "\n")
                print("Student details saved to students_list.txt")

            remove_duplicates(students_list_file_path)

            with open(students_details_file_path, "a") as students_details_file:
                students_details_file.write("\n".join([f"{name} {father_name.capitalize()} {class_section}:{email}" for name, email in zip(student_data["Name"], student_data["Parent Email"])]) + "\n")
                print("Student details saved to students_details.txt")

            remove_duplicates(students_details_file_path)

            remove_duplicates_from_excel(student_file_path)

    except KeyboardInterrupt:
        print("\nDatabase creation interrupted.")

if __name__ == "__main__":
    create_student_database()
