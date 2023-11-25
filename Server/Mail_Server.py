import pickle
import socket
import threading

import mysql.connector

class EmailServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('192.168.1.4', 1234)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen()
        print('Server is listening...')
        self.is_running = False
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="mail_program"
        )
        self.mycursor = self.mydb.cursor()
        self.active_user = set()

    def start_server(self):
        self.is_running = True
        while self.is_running:
            client_socket, client_address = self.server_socket.accept()
            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.daemon = True
            thread.start()

    def stop_server(self):
        self.is_running = False
        self.server_socket.close()

    def handle_client(self, client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            parts = message.split('\n')

            if parts[0] == 'CREATE_ACCOUNT':
                _, username, password = parts[:3]
                self.create_account(username, password)
                response = 'Account created successfully.'
                client_socket.sendall(response.encode('utf-8'))


            elif parts[0] == 'SEND_EMAIL':
                _, username, recipient_email, subject_email, time_sending = parts[:5]
                email_content = ' '.join(parts[5:])
                check = self.receive_email(username, recipient_email, subject_email, email_content, time_sending)

                if check:
                    response = 'Gửi thành công.'
                    client_socket.sendall(response.encode('utf-8'))
                else:
                    response = 'Người dùng không tồn tại.'
                    client_socket.sendall(response.encode('utf-8'))

            elif parts[0] == 'refresh_inbox':
                _, email_entry, email_type = parts[:3]
                response = self.refresh_inbox(email_entry, email_type)
                data_bytes = pickle.dumps(response)
                client_socket.sendall(data_bytes)

            elif parts[0] == 'get_user_list':
                response = self.get_user_list()
                data_bytes = pickle.dumps(response)
                client_socket.sendall(data_bytes)

            elif parts[0] == "check_login":
                _, email, password = parts[:3]
                response = self.check_login(email, password)
                client_socket.sendall(response.encode('utf-8'))


        client_socket.close()

    def create_account(self, username, password):
        # Ví dụ về thêm dữ liệu: INSERT
        sql = "INSERT INTO account (email, password) VALUES (%s, %s)"
        val = (username, password)

        self.mycursor.execute(sql, val)

        self.mydb.commit()

    def receive_email(self, username, recipient_email, subject_email, email_content, time_sending):
        sql_id_email_sender = "select id from account where email = '{}'".format(username)
        sql_id_email_rev = "select id from account where email = '{}'".format(recipient_email)
        self.mycursor.execute(sql_id_email_sender)
        id_email_sender = self.mycursor.fetchone()
        self.mycursor.execute(sql_id_email_rev)
        id_email_rev = self.mycursor.fetchone()

        print(time_sending)

        if (id_email_sender and id_email_rev):

            sql = "INSERT INTO mail(sender_id, recipient_id, subject, content, time) VALUES (%s, %s, %s, %s, %s)"
            val = (id_email_sender[0], id_email_rev[0], subject_email, email_content, time_sending)

            self.mycursor.execute(sql, val)
            self.mydb.commit()
            return True
        else:
            return False

    def refresh_inbox(self, email_entry, email_type):

        if email_type == "sender":
            sql = """
                    SELECT 
                        mail.mail_id AS mail_id,
                        mail.subject AS email_subject,
                        mail.content AS email_content,
                        mail.time AS email_time,                        
                        recipient.email AS recipient_email
                    FROM 
                        mail
                    INNER JOIN 
                        account AS sender ON mail.sender_id = sender.id
                    INNER JOIN 
                        account AS recipient ON mail.recipient_id = recipient.id
                    WHERE 
                        sender.email = '{}'""".format(email_entry)
            # print(sql)
            self.mycursor.execute(sql)

            result = self.mycursor.fetchall()
        else:
            sql = """
                    SELECT 
                        mail.mail_id AS mail_id,
                        mail.subject AS email_subject,
                        mail.content AS email_content,
                        mail.time AS email_time,
                        sender.email AS sender_email                       
                    FROM 
                        mail
                    INNER JOIN 
                        account AS sender ON mail.sender_id = sender.id
                    INNER JOIN 
                        account AS recipient ON mail.recipient_id = recipient.id
                    WHERE 
                        recipient.email = '{}'""".format(email_entry)

            self.mycursor.execute(sql)

            result = self.mycursor.fetchall()
        print(result)
        return result

    def get_user_list(self):
        sql = "Select * from account"
        self.mycursor.execute(sql)

        user_list = self.mycursor.fetchall()
        print(user_list)
        print(self.active_user)
        return user_list

    def get_data_all(self, id):
        sql = """
            SELECT
                mail.mail_id AS mail_id,
                mail.subject AS email_subject,
                mail.content AS email_content,
                mail.time AS email_time,
                recipient.email AS rev_email
            FROM
                mail
            INNER JOIN ACCOUNT AS sender
            ON
                mail.sender_id = sender.id
            INNER JOIN ACCOUNT AS recipient
            ON
                mail.recipient_id = recipient.id
            WHERE
                sender.id = '{}'
        """.format(id)
        self.mycursor.execute(sql)
        result = self.mycursor.fetchall()
        return result

    def check_login(self, email, password):

        sql = "Select * from account where email = %s and password = %s"
        val = (email, password)
        self.mycursor.execute(sql, val)
        result = self.mycursor.fetchone()

        if result:
            self.active_user.add(email)
            return "True"
        else:
            return "False"


if __name__ == '__main__':
    email_server = EmailServer()
    email_server.get_user_list()
    # email_server.start_server()  # Khởi động server
