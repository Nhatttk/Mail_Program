import re
import socket
from tkinter import messagebox
import tkinter as tk

from test_gui import EmailApp

class EmailClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 1234)
        self.client_socket.connect(self.server_address)

        self.root = tk.Tk()
        self.root.title("Login")

        self.frameLogin = tk.Frame(self.root)
        self.frameLogin.grid(padx=20, pady=20)

        # Tạo và định vị các thành phần
        tk.Label(self.frameLogin, text="Email:").grid(row=0, padx=10, pady=5)
        self.email_entry = tk.Entry(self.root)
        self.email_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Mật khẩu:").grid(row=1, padx=10, pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        self.login_button = tk.Button(self.root, text="Login", command=self.validate_login)
        self.login_button.grid(row=2, column=1, columnspan=1, pady=10)

        self.button_create_account = tk.Button(self.root, text="Create Account", command=self.create_account)
        self.button_create_account.grid(row=2, column=0, columnspan=1, pady=10, sticky=tk.W + tk.E)

        # Chạy chương trình
        self.root.mainloop()

    def validate_login(self):

        email = self.email_entry.get()
        password = self.password_entry.get()

        message = f"check_login\n{email}\n{password}"
        self.client_socket.sendall(message.encode('utf-8'))

        data = self.client_socket.recv(1024)
        message = data.decode('utf-8')

        if message == "True":
            messagebox.showinfo("Thông báo", "Đăng nhập thành công")
            self.root.withdraw()
            email_app_window = tk.Toplevel()
            app = EmailApp(email_app_window, email, self.client_socket)
        elif message == "False":
            messagebox.showinfo("Thông báo", "Thông tin tài khoản hoặc mật khẩu không chính xác")
        else:
            messagebox.showinfo("Thông báo", "Lỗi không xác định")



    def is_valid_email(self,email):
        # Mẫu biểu thức chính quy kiểm tra địa chỉ email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        # So khớp với mẫu
        if re.match(email_pattern, email):
            return True
        else:
            return False

    def create_account(self):
        username = self.email_entry.get()
        password = self.password_entry.get()

        if self.is_valid_email(username):
            message = f'CREATE_ACCOUNT\n{username}\n{password}'
            self.client_socket.sendall(message.encode('utf-8'))
            data = self.client_socket.recv(1024)
            messagebox.showinfo('Server Response', data.decode('utf-8'))
        else:
            messagebox.showinfo("Thông báo", "Không đúng định dạng email!")



if __name__ == '__main__':
    EmailClient()






