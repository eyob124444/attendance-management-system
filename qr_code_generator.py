import qrcode

def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

def main():
    with open("students_list.txt", "r") as file:
        students = file.read().splitlines()

    for student in students:
        data = f"STUDENT: {student}"
        filename = f"qrcodes/{student}.png"
        generate_qr_code(data, filename)

if __name__ == "__main__":
    main()
