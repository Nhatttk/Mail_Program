import threading
import tkinter as tk
from tkinter import messagebox, font, ttk

from Mail_Server import EmailServer


class EmailServerGUI:
    def __init__(self, root, email_server):
        self.root = root
        self.email_server = email_server

        self.label = tk.Label(root, text="Các tài khoản user")
        self.label.pack(padx=10, pady=10)

        self.user_listbox = tk.Listbox(root, height=20, width=80)
        myFonts = font.Font(family="Arial", size=12)
        self.user_listbox.config(font=myFonts)
        self.user_listbox.pack(padx=10, pady=10)
        self.user_listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        self.refresh_list_user = tk.Button(root, text="Tải lại danh sách", command=self.show_user_list)
        self.refresh_list_user.pack(padx=10, pady=10)

        self.start_button = tk.Button(root, text="Bật Server", command=self.start_server)
        self.start_button.pack(padx=10, pady=10)

        self.stop_button = tk.Button(root, text="Tắt Server", command=self.stop_server)
        self.stop_button.pack(padx=10, pady=10)

    def start_server(self):
        self.email_server_thread = threading.Thread(target=self.email_server.start_server)
        self.email_server_thread.start()
        # self.show_user_list()
        messagebox.showinfo("Thông báo", "Server đã được bật thành công.")

    def stop_server(self):
        self.email_server.stop_server()

    def show_user_list(self):
        user_list = self.email_server.get_user_list()
        active_user = self.email_server.active_user
        self.user_listbox.delete(0, tk.END)
        for user in user_list:
            if user[1] in active_user:
                self.user_listbox.insert(tk.END, user[1] + " (dang hoat dong)")
            else:
                self.user_listbox.insert(tk.END, user[1])

    def on_listbox_select(self, event):
        # Lấy chỉ số của item được chọn
        selected_index_tuple = self.user_listbox.curselection()

        if selected_index_tuple:
            selected_index = selected_index_tuple[0]
            id = self.email_server.get_user_list()[selected_index][0]
            print(id)
            result = self.email_server.get_data_all(id)
            print(result)
            self.user_data_gui(result)

    def user_data_gui(self, data):
        popup_window = tk.Toplevel(self.root)
        popup_window.title("Thông tin chi tiết")

        # Tạo Listbox để hiển thị nội dung
        listbox = tk.Listbox(popup_window, selectmode=tk.SINGLE,  width=80, height=10)
        listbox.pack(expand=True, fill='both')

        # Thêm nội dung vào Listbox
        for item in data:
            listbox.insert(tk.END, item)

        # Thêm thanh cuộn
        scrollbar = ttk.Scrollbar(popup_window, orient=tk.VERTICAL, command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        # Khi chọn một item, gọi hàm callback
        # listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        # Nút đóng
        # close_button = ttk.Button(self, text="Đóng", command=self.destroy)
        # close_button.pack(pady=10)


if __name__ == "__main__":
    email_server = EmailServer()

    root = tk.Tk()
    app = EmailServerGUI(root, email_server)
    app.show_user_list()
    root.mainloop()
