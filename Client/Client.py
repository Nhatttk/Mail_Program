import os
import pickle
import socket
import threading
import tkinter as tk
from tkinter import messagebox, Listbox
import re
import datetime

from test_gui import EmailApp


def loginFrame():

    global email_entry, password_entry, frameLogin, root

    root = tk.Tk()
    root.title("Login")

    frameLogin = tk.Frame(root)
    frameLogin.grid(padx=20, pady=20)



    # Tạo và định vị các thành phần
    tk.Label(frameLogin, text="Email:").grid(row=0, padx=10, pady=5)
    email_entry = tk.Entry(root)
    email_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Mật khẩu:").grid(row=1, padx=10, pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    login_button = tk.Button(root, text="Login", command=validate_login)
    login_button.grid(row=2, column=1, columnspan=1, pady=10)

    button_create_account = tk.Button(root, text="Create Account", command=create_account)
    button_create_account.grid(row=2, column=0,columnspan=1, pady=10, sticky=tk.W + tk.E)

    # Chạy chương trình
    root.mainloop()

def validate_login():

    email = email_entry.get()
    password = password_entry.get()

    message = f"check_login {email} {password}"
    client_socket.sendall(message.encode('utf-8'))

    data= client_socket.recv(1024)
    message = data.decode('utf-8')


    if message == "True":
        messagebox.showinfo("Thông báo", "Đăng nhập thành công")
        root2 = tk.Toplevel()
        app = EmailApp(root2, email, client_socket)
    elif message == "False":
        messagebox.showinfo("Thông báo", "Thông tin tài khoản hoặc mật khẩu không chính xác")



def show_new_frame():

    global entry_recipient_email, entry_subject_email
    global text_email
    global inbox_listbox


    root = tk.Tk()
    root.title("Mail Client")

    frame = tk.Frame(root)
    frame.pack(padx=20, pady=20)

    label_recipient_email = tk.Label(frame, text="Recipient Email:")
    label_recipient_email.grid(row=1, column=0, sticky=tk.W, pady=5)
    entry_recipient_email = tk.Entry(frame)
    entry_recipient_email.grid(row=1, column=1, pady=5)

    label_subject_email = tk.Label(frame, text="Subjects:")
    label_subject_email.grid(row=2, column=0, sticky=tk.W, pady=5)
    entry_subject_email = tk.Entry(frame)
    entry_subject_email.grid(row=2, column=1, pady=5)

    label_email = tk.Label(frame, text="Email Content:")
    label_email.grid(row=4, column=0, sticky=tk.W, pady=5)
    text_email = tk.Text(frame, width=40, height=10)
    text_email.grid(row=5, column=0, columnspan=2, pady=5)

    button_send_email = tk.Button(frame, text="Send Email", command=send_email)
    button_send_email.grid(row=6, column=0, columnspan=2, pady=10, sticky=tk.W + tk.E)

    button_refresh_inbox = tk.Button(frame, text="Refresh Inbox", command=refresh_inbox)
    button_refresh_inbox.grid(row=7, column=0, columnspan=2, pady=10, sticky=tk.W + tk.E)

    inbox_label = tk.Label(frame, text="Inbox:")
    inbox_label.grid(row=8, column=0, sticky=tk.W, pady=5)
    inbox_listbox = Listbox(frame, width=40, height=10)
    inbox_listbox.grid(row=9, column=0, columnspan=2, pady=5)
    inbox_listbox.bind("<<ListboxSelect>>", on_listbox_select)

    refresh_inbox()

    root.mainloop()
def create_account():
    username = email_entry.get()
    password = password_entry.get()

    if is_valid_email(username):
        message = f'CREATE_ACCOUNT {username} {password}'
        client_socket.sendall(message.encode('utf-8'))
        data = client_socket.recv(1024)
        messagebox.showinfo('Server Response', data.decode('utf-8'))
    else:
        messagebox.showinfo("Thông báo", "Không đúng định dạng email!")


def send_email():
    username = email_entry.get()
    recipient_email = entry_recipient_email.get()

    # Lấy thời gian hiện tại
    current_time = datetime.datetime.now()

    # Chuyển đổi thời gian thành chuỗi theo định dạng mong muốn (ví dụ: yyyy-mm-dd HH:MM:SS)
    time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")

    email_subject = entry_subject_email.get()
    email_content = text_email.get("1.0", tk.END)

    message = f'SEND_EMAIL {username} {recipient_email} {email_subject} {email_content} {time_string}'
    client_socket.sendall(message.encode('utf-8'))
    data= client_socket.recv(1024)
    messagebox.showinfo('Server Response', data.decode('utf-8'))


def refresh_inbox():
    inbox_listbox.delete(0, tk.END)
    message = f'refresh_inbox {email_entry.get()}'
    client_socket.sendall(message.encode('utf-8'))
    data = client_socket.recv(1024)
    # messagebox.showinfo('Server Response', data.decode('utf-8'))
    data_bytes = pickle.loads(data)
    for x in data_bytes:
        inbox_listbox.insert(tk.END, x)


def is_valid_email(email):
    # Mẫu biểu thức chính quy kiểm tra địa chỉ email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # So khớp với mẫu
    if re.match(email_pattern, email):
        return True
    else:
        return False

def on_listbox_select(event):
    # Lấy chỉ số của item được chọn
    selected_index = inbox_listbox.curselection()

    # Lấy giá trị của item được chọn
    selected_value = inbox_listbox.get(selected_index)

    # Hiển thị giá trị của item được chọn
    messagebox.showinfo("Inbox", selected_value)

def main():
    global client_socket
    global server_address



    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 1234)
    client_socket.connect(server_address)

    loginFrame()

    client_socket.close()


if __name__ == "__main__":
    # thread = threading.Thread(target=main())
    # thread.start()
    main()
