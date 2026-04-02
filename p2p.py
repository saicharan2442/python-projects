import socket
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext
from PIL import Image, ImageTk
import os
import mimetypes

# ---------- CONFIG ----------
UDP_PORT = 50000
TCP_PORT = 50001
BUFFER = 4096

clients = set()
username = ""
my_ip = ""

# ---------- FILE TYPE ----------
def get_file_type(file):
    mime, _ = mimetypes.guess_type(file)
    if mime and mime.startswith("image"):
        return "image"
    return "file"

# ---------- NETWORK ----------
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

# ---------- SAFE SEND ----------
def send_with_header(sock, data_bytes):
    length = len(data_bytes)
    sock.send(f"{length:<10}".encode())
    sock.send(data_bytes)

def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            break
        data += chunk
    return data

# ---------- DISCOVERY ----------
def listen_users():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("", UDP_PORT))

    while True:
        data, addr = udp.recvfrom(1024)
        name = data.decode()
        if addr[0] != my_ip:
            clients.add((addr[0], name))

def broadcast():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        udp.sendto(username.encode(), ("<broadcast>", UDP_PORT))
        threading.Event().wait(2)

# ---------- SERVER ----------
def start_server():
    server = socket.socket()
    server.bind(("0.0.0.0", TCP_PORT))
    server.listen(5)

    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle_client, args=(conn,)).start()

def handle_client(conn):
    try:
        header_len = int(conn.recv(10).decode().strip())
        header = recv_exact(conn, header_len).decode()
        parts = header.split("|")

        if parts[0] == "MSG":
            show_text(f"{parts[1]}: {parts[2]}")

        elif parts[0] == "FILE":
            sender, filename, size = parts[1], parts[2], int(parts[3])

            path = os.path.join("received", filename)
            os.makedirs("received", exist_ok=True)

            remaining = size
            with open(path, "wb") as f:
                while remaining > 0:
                    chunk = conn.recv(min(BUFFER, remaining))
                    if not chunk:
                        break
                    f.write(chunk)
                    remaining -= len(chunk)

            show_file(sender, path, filename)

    except Exception as e:
        print("Error:", e)

    conn.close()

# ---------- SEND ----------
def send_message(event=None):
    msg = entry.get()
    if not msg:
        return

    for ip, _ in clients:
        try:
            s = socket.socket()
            s.connect((ip, TCP_PORT))

            data = f"MSG|{username}|{msg}".encode()
            send_with_header(s, data)

            s.close()
        except:
            pass

    show_text(f"You: {msg}")
    entry.delete(0, tk.END)

def send_file():
    path = filedialog.askopenfilename()
    if not path:
        return

    filename = os.path.basename(path)
    size = os.path.getsize(path)

    for ip, _ in clients:
        try:
            s = socket.socket()
            s.connect((ip, TCP_PORT))

            header = f"FILE|{username}|{filename}|{size}".encode()
            send_with_header(s, header)

            with open(path, "rb") as f:
                while True:
                    chunk = f.read(BUFFER)
                    if not chunk:
                        break
                    s.sendall(chunk)

            s.close()
        except:
            pass

    show_file("You", path, filename)

# ---------- UI DISPLAY ----------
def show_text(message):
    chat_box.insert(tk.END, message + "\n")
    chat_box.yview(tk.END)

def show_file(sender, path, filename):
    chat_box.insert(tk.END, f"{sender} sent:\n")

    if get_file_type(filename) == "image":
        img = Image.open(path)
        img.thumbnail((200, 200))
        img_tk = ImageTk.PhotoImage(img)

        chat_box.image_create(tk.END, image=img_tk)
        chat_box.insert(tk.END, "\n")

        if not hasattr(chat_box, "images"):
            chat_box.images = []
        chat_box.images.append(img_tk)
    else:
        def open_file():
            os.startfile(path)

        btn = tk.Button(chat_box, text=f"📎 {filename}", command=open_file)
        chat_box.window_create(tk.END, window=btn)
        chat_box.insert(tk.END, "\n")

    chat_box.yview(tk.END)

# ---------- UI ----------
def build_chat_ui():
    global entry, chat_box

    root = tk.Tk()
    root.title(f"P2P Chat - {username}")
    root.geometry("500x600")

    chat_box = scrolledtext.ScrolledText(root)
    chat_box.pack(fill="both", expand=True)

    entry = tk.Entry(root)
    entry.pack(fill="x")

    entry.bind("<Return>", send_message)  # 🔥 ENTER KEY FIX

    btn_frame = tk.Frame(root)
    btn_frame.pack()

    tk.Button(btn_frame, text="Send", command=send_message).pack(side="left")
    tk.Button(btn_frame, text="📎 File", command=send_file).pack(side="left")

    root.mainloop()

# ---------- LOGIN ----------
def start_chat():
    global username, my_ip

    username = name_entry.get()
    if not username:
        return

    my_ip = get_ip()
    login.destroy()

    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=listen_users, daemon=True).start()
    threading.Thread(target=broadcast, daemon=True).start()

    build_chat_ui()

login = tk.Tk()
login.title("Enter Name")
login.geometry("300x150")

tk.Label(login, text="Enter your name").pack(pady=10)
name_entry = tk.Entry(login)
name_entry.pack(pady=5)

tk.Button(login, text="Start Chat", command=start_chat).pack(pady=10)

login.mainloop()