import datetime
import pickle
import tkinter as tk
from tkinter import ttk, font
from tkinter import messagebox


class EmailApp:
    def __init__(self, master, username, client_socket):
        self.data_bytes = None
        self.master = master
        self.username = username
        self.client_socket = client_socket
        self.master.title("Email Client - " + username)
        self.master.geometry("800x600")

        # Tạo thanh menu bên trái
        self.menu_frame = ttk.Frame(self.master, width=200)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.menu_tree = ttk.Treeview(self.menu_frame, selectmode="browse")
        self.menu_tree.heading("#0", text="Menu")
        self.menu_tree.insert("", "end", "inbox", text="Hộp thư đến", tags=("menu_item",))
        self.menu_tree.insert("", "end", "outbox", text="Hộp thư đi", tags=("menu_item",))
        self.menu_tree.insert("", "end", "send_mail", text="Gửi mail", tags=("menu_item",))
        self.menu_tree.tag_configure("menu_item", font=('Helvetica', 10, 'bold'))
        self.menu_tree.bind("<ButtonRelease-1>", self.menu_item_clicked)
        self.menu_tree.pack(expand=True, fill=tk.Y)

        # Tạo nội dung bên phải với ttk.Notebook
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # inbox_frame
        self.inbox_frame = ttk.Frame(self.notebook)
        self.inbox_text = tk.Listbox(self.inbox_frame, height=20, width=80)
        myFonts = font.Font(family="Arial", size=12)
        self.inbox_text.config(font=myFonts)
        self.inbox_text.pack(padx=10, pady=10)

        self.button_refresh_inbox = tk.Button(self.inbox_frame, text="Tải lại",
                                              command=lambda: self.refresh_inbox(self.inbox_text, "rev"))
        self.button_refresh_inbox.pack(pady=10, side=tk.TOP)
        self.notebook.add(self.inbox_frame, text="Hộp thư đến")

        # outbox_frame
        self.outbox_frame = ttk.Frame(self.notebook)
        self.outbox_text = tk.Listbox(self.outbox_frame, height=20, width=80)
        myFonts2 = font.Font(family="Arial", size=12)
        self.outbox_text.config(font=myFonts2)
        self.outbox_text.pack(padx=10, pady=10)

        self.button_refresh_outbox = tk.Button(self.outbox_frame, text="Tải lại",
                                               command=lambda: self.refresh_inbox(self.outbox_text, "sender"))
        self.button_refresh_outbox.pack(pady=10, side=tk.TOP)
        self.notebook.add(self.outbox_frame, text="Hộp thư đi")

        self.send_frame = ttk.Frame(self.notebook)
        self.label_recipient_email = tk.Label(self.send_frame, text="Email người nhận:")
        self.label_recipient_email.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_recipient_email = tk.Entry(self.send_frame)
        self.entry_recipient_email.grid(row=1, column=1, pady=5)

        self.label_subject_email = tk.Label(self.send_frame, text="Tiêu đề:")
        self.label_subject_email.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_subject_email = tk.Entry(self.send_frame)
        self.entry_subject_email.grid(row=2, column=1, pady=5)

        self.label_email = tk.Label(self.send_frame, text="Nội dung:")
        self.label_email.grid(row=4, column=0, sticky=tk.W, pady=5)
        self.text_email = tk.Text(self.send_frame, width=40, height=10)
        self.text_email.grid(row=5, column=0, columnspan=2, pady=5)

        self.button_send_email = tk.Button(self.send_frame, text="Gửi Email", command=self.send_email)
        self.button_send_email.grid(row=6, column=0, columnspan=2, pady=10, sticky=tk.W + tk.E)
        self.notebook.add(self.send_frame, text="Gửi mail")

    def menu_item_clicked(self, event):
        item = self.menu_tree.selection()[0]
        if item == "inbox":
            self.notebook.select(0)
            self.refresh_inbox(self.inbox_text, "rev")
        elif item == "outbox":
            self.notebook.select(1)
            self.refresh_inbox(self.outbox_text, "sender")
        elif item == "send_mail":
            self.notebook.select(2)

    def send_email(self):
        username = self.username
        recipient_email = self.entry_recipient_email.get()

        # Lấy thời gian hiện tại
        current_time = datetime.datetime.now()

        # Chuyển đổi thời gian thành chuỗi theo định dạng mong muốn (ví dụ: yyyy-mm-dd HH:MM:SS)
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")

        email_subject = self.entry_subject_email.get()
        email_content = self.text_email.get("1.0", tk.END)

        message = f'SEND_EMAIL\n{username}\n{recipient_email}\n{email_subject}\n{time_string}\n{email_content}'
        self.client_socket.sendall(message.encode('utf-8'))
        data = self.client_socket.recv(1024)
        messagebox.showinfo('Server Response', data.decode('utf-8'))

    def refresh_inbox(self, listbox, email_type):

        listbox.delete(0, tk.END)
        message = f'refresh_inbox\n{self.username}\n{email_type}'
        self.client_socket.sendall(message.encode('utf-8'))
        data = self.client_socket.recv(1024)
        # messagebox.showinfo('Server Response', data.decode('utf-8'))
        self.data_bytes = pickle.loads(data)  # Lưu data_bytes vào biến instance
        for email_info in self.data_bytes:
            display_text = f"{email_info[1]} - {email_info[2]}"
            listbox.insert(tk.END, display_text)

        # Gán sự kiện click cho listbox khi refresh
        self.bind_listbox_event(listbox, email_type)

    def on_listbox_click(self, event, listbox, email_type):
        selected_index_tuple = listbox.curselection()
        if selected_index_tuple:
            selected_index = selected_index_tuple[0]
            selected_item = listbox.get(selected_index)
            email_info = self.data_bytes[selected_index]
            self.create_popup_window(email_info, email_type)

    def bind_listbox_event(self, listbox, email_type):
        listbox.bind("<ButtonRelease-1>", lambda event: self.on_listbox_click(event, listbox, email_type))

    def create_popup_window(self, email_info, email_type):
        popup_window = tk.Toplevel(self.master)
        popup_window.title("Thông tin chi tiết")

        label_id = tk.Label(popup_window, text=f"Mail ID: {email_info[0]}")
        label_id.pack(pady=5)

        label_subject = tk.Label(popup_window, text=f"Subject: {email_info[1]}")
        label_subject.pack(pady=5)

        label_content = tk.Label(popup_window, text="Nội dung:")
        label_content.pack(pady=5)

        text_content = tk.Text(popup_window, wrap=tk.WORD, width=40, height=10)
        text_content.insert(tk.END, email_info[2])
        text_content.pack(pady=5)

        label_time = tk.Label(popup_window, text=f"Thời gian: {email_info[3]}")
        label_time.pack(pady=5)

        if email_type == "sender" :
            label_sender = tk.Label(popup_window, text=f"Người nhận: {email_info[4]}")
            label_sender.pack(pady=5)
        elif email_type == "rev":
            label_sender = tk.Label(popup_window, text=f"Người gửi: {email_info[4]}")
            label_sender.pack(pady=5)

