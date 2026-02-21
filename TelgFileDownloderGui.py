import asyncio
import os
import re
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument
import subprocess
import sys

# -------- CONFIG --------
api_id = 38615406
api_hash = "b7fbc1d82a0fb6945c69f3f3c375bea1"
MAX_RESULTS = 10000
BASE_DOWNLOAD_DIR = "downloads"
# ------------------------

results = []

# -------- ASYNC LOOP THREAD (FIXED STRUCTURE) --------
loop = asyncio.new_event_loop()

def start_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=start_loop, daemon=True).start()

client = TelegramClient("session", api_id, api_hash, loop=loop)


# ---------- Helpers ----------
def sanitize_folder_name(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]', "_", name.strip())
    return re.sub(r"\s+", "_", name).lower()


def open_file(path):
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform.startswith("darwin"):
        subprocess.call(("open", path))
    else:
        subprocess.call(("xdg-open", path))


def simple_input_dialog(title, prompt):
    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.geometry("350x160")
    dialog.configure(bg="#1e1e2f")
    dialog.grab_set()

    tk.Label(dialog, text=prompt,
             bg="#1e1e2f", fg="white").pack(pady=10)

    entry = tk.Entry(dialog, width=30)
    entry.pack(pady=5)

    result = {"value": None}

    def submit():
        result["value"] = entry.get().strip()
        dialog.destroy()

    ttk.Button(dialog, text="Submit", command=submit).pack(pady=10)

    root.wait_window(dialog)
    return result["value"]


# ---------- LOGIN HANDLER ----------
async def ensure_login():
    await client.connect()

    if await client.is_user_authorized():
        return

    login_data = {"phone": None, "code": None}

    def login_window():
        dialog = tk.Toplevel(root)
        dialog.title("Telegram Login")
        dialog.geometry("400x250")
        dialog.configure(bg="#1e1e2f")
        dialog.grab_set()

        tk.Label(dialog, text="Telegram Login",
                 bg="#1e1e2f", fg="white",
                 font=("Segoe UI", 14, "bold")).pack(pady=10)

        tk.Label(dialog, text="Phone Number (with country code)",
                 bg="#1e1e2f", fg="#bbbbff").pack()

        phone_entry = tk.Entry(dialog, width=30)
        phone_entry.pack(pady=5)

        tk.Label(dialog, text="OTP Code",
                 bg="#1e1e2f", fg="#bbbbff").pack()

        code_entry = tk.Entry(dialog, width=30, state="disabled")
        code_entry.pack(pady=5)

        status_label = tk.Label(dialog,
                                text="",
                                bg="#1e1e2f",
                                fg="#00e5ff")
        status_label.pack(pady=5)

        async def send_otp():
            phone = phone_entry.get().strip()
            if not phone:
                status_label.config(text="Enter phone number", fg="red")
                return

            login_data["phone"] = phone
            status_label.config(text="Sending OTP...", fg="#ffcc00")

            await client.send_code_request(phone)

            code_entry.config(state="normal")
            status_label.config(text="OTP sent ✔", fg="#00ff99")

        async def verify():
            code = code_entry.get().strip()
            if not code:
                status_label.config(text="Enter OTP", fg="red")
                return

            login_data["code"] = code
            status_label.config(text="Verifying...", fg="#ffcc00")

            try:
                await client.sign_in(login_data["phone"], code)
                status_label.config(text="Login Successful ✔", fg="#00ff99")
                dialog.destroy()
            except Exception as e:
                status_label.config(text="Invalid OTP", fg="red")

        def send_otp_thread():
            asyncio.run_coroutine_threadsafe(send_otp(), loop)

        def verify_thread():
            asyncio.run_coroutine_threadsafe(verify(), loop)

        ttk.Button(dialog, text="Send OTP",
                   command=send_otp_thread).pack(pady=5)

        ttk.Button(dialog, text="Login",
                   command=verify_thread).pack(pady=5)

        root.wait_window(dialog)

    # Open login window in main thread
    root.after(0, login_window)

    # Wait until login completes
    while not await client.is_user_authorized():
        await asyncio.sleep(0.5)

# ---------- SEARCH ----------
async def search_files(channel_username, keyword):
    global results
    results = []

    def clear_ui():
        results_listbox.delete(0, tk.END)
        files_count_label.config(text="📦 Total Files: 0")

    root.after(0, clear_ui)

    await ensure_login()

    fetch_all = keyword.strip().lower() == "all"

    if fetch_all:
        message_iterator = client.iter_messages(channel_username)
    else:
        message_iterator = client.iter_messages(channel_username, search=keyword)

    async for message in message_iterator:
        if len(results) >= MAX_RESULTS:
            break

        if (
            not message.media
            or not isinstance(message.media, MessageMediaDocument)
            or not message.file
            or not message.file.name
        ):
            continue

        results.append(message)
        size_mb = message.file.size / (1024 * 1024)

        def insert_item():
            results_listbox.insert(
                tk.END,
                f"{len(results)}. {message.file.name} ({size_mb:.2f} MB)"
            )
            files_count_label.config(
                text=f"📦 Total Files: {len(results)}"
            )

        root.after(0, insert_item)

    if fetch_all:
        root.after(0, lambda: set_status("Showing ALL files ✔", "#00ff99"))
    else:
        root.after(0, lambda: set_status("Search Completed ✔", "#00ff99"))

# ---------- DOWNLOAD ----------
async def download_selected(indexes, download_dir):
    await ensure_login()

    for idx in indexes:
        message = results[idx]
        filename = message.file.name

        root.after(0, lambda f=filename:
                   set_status(f"Downloading: {f}", "#00e5ff"))

        await client.download_media(
            message,
            file=download_dir,
            progress_callback=lambda c, t: update_progress(c, t)
        )

    root.after(0, lambda: set_status("Download Completed ✔", "#00ff99"))
    root.after(0, lambda: progress_bar.config(value=0))
    root.after(0, lambda: messagebox.showinfo(
        "Success", "Downloads completed successfully!"
    ))


# ---------- PROGRESS ----------
def update_progress(current, total):
    percent = int(current * 100 / total)

    def update_ui():
        progress_bar["value"] = percent
        set_status(f"Downloading... {percent}%", "#ffcc00")

    root.after(0, update_ui)


# ---------- Button Actions ----------
def start_search():
    channel = channel_entry.get().strip()
    keyword = keyword_entry.get().strip()

    if not channel or not keyword:
        messagebox.showerror("Error", "Please enter channel and keyword")
        return

    set_status("Searching...", "#ffcc00")

    asyncio.run_coroutine_threadsafe(
        search_files(channel, keyword),
        loop
    )


def start_download():
    selected = results_listbox.curselection()

    if not selected:
        messagebox.showerror("Error", "Select at least one file")
        return

    keyword = keyword_entry.get().strip()

    if keyword.lower() == "all":
        folder = "all_files"
    else:
        folder = sanitize_folder_name(keyword)

    download_dir = os.path.join(BASE_DOWNLOAD_DIR, folder)
    os.makedirs(download_dir, exist_ok=True)

    asyncio.run_coroutine_threadsafe(
        download_selected(selected, download_dir),
        loop
    )

# ---------- VIEW DOWNLOADS ----------
def view_downloads():
    download_window = tk.Toplevel(root)
    download_window.title("Downloaded Files")
    download_window.geometry("800x520")
    download_window.configure(bg="#1e1e2f")

    style = ttk.Style()
    style.theme_use("default")

    # Treeview styling
    style.configure("Treeview",
                    background="#2b2b3c",
                    foreground="white",
                    fieldbackground="#2b2b3c",
                    rowheight=28,
                    font=("Segoe UI", 10))

    style.map("Treeview",
              background=[("selected", "#3a86ff")])

    style.configure("Treeview.Heading",
                    font=("Segoe UI", 11, "bold"),
                    background="#1e1e2f",
                    foreground="cyan")

    container = tk.Frame(download_window, bg="#1e1e2f")
    container.pack(fill="both", expand=True, padx=15, pady=15)

    tree = ttk.Treeview(container, show="tree")
    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    if not os.path.exists(BASE_DOWNLOAD_DIR):
        os.makedirs(BASE_DOWNLOAD_DIR)

    # Insert root folder
    root_node = tree.insert(
        "",
        "end",
        text=f"📂 {os.path.basename(BASE_DOWNLOAD_DIR)}",
        open=True,
        values=(BASE_DOWNLOAD_DIR,)
    )

    def insert_items(parent, path):
        items = sorted(os.listdir(path))

        for item in items:
            full_path = os.path.join(path, item)

            if os.path.isdir(full_path):
                node = tree.insert(
                    parent,
                    "end",
                    text=f"📁 {item}",
                    open=False,
                    values=(full_path,)
                )
                insert_items(node, full_path)
            else:
                tree.insert(
                    parent,
                    "end",
                    text=f"📄 {item}",
                    values=(full_path,)
                )

    insert_items(root_node, BASE_DOWNLOAD_DIR)

    def open_selected(event=None):
        selected = tree.selection()
        if not selected:
            return

        item = selected[0]
        full_path = tree.item(item, "values")[0]

        if os.path.isfile(full_path):
            open_file(full_path)
        else:
            tree.item(item, open=not tree.item(item, "open"))

    tree.bind("<Double-1>", open_selected)
    

    ttk.Button(download_window,
               text="Open Selected",
               command=open_selected).pack(pady=10)

# ---------- STATUS ----------
def set_status(text, color):
    status_label.config(text=text, fg=color)


# ---------- GUI ----------
root = tk.Tk()
root.title("Telegram File Downloader")
root.geometry("1080x577")
root.configure(bg="#141421")

sidebar = tk.Frame(root, bg="#1e1e2f", width=200)
sidebar.pack(side="left", fill="y")

tk.Label(sidebar, text="📥 Downloader",
         bg="#1e1e2f", fg="white",
         font=("Segoe UI", 14, "bold")).pack(pady=20)

ttk.Button(sidebar, text="📂 View Downloads",
           command=view_downloads).pack(pady=10, padx=20, fill="x")

main_frame = tk.Frame(root, bg="#141421")
main_frame.pack(side="right", expand=True, fill="both", padx=20, pady=20)

card = tk.Frame(main_frame, bg="#1e1e2f")
card.pack(fill="both", expand=True, padx=10, pady=10)

tk.Label(card, text="Telegram File Downloader",
         bg="#1e1e2f", fg="white",
         font=("Segoe UI", 18, "bold")).pack(pady=15)

# ---------- SIDE BY SIDE INPUT SECTION ----------

input_container = tk.Frame(card, bg="#1e1e2f")
input_container.pack(fill="x", padx=40, pady=20)

input_container.columnconfigure(0, weight=1)
input_container.columnconfigure(1, weight=1)

# Channel Box
channel_wrapper = tk.Frame(
    input_container,
    bg="#2a2a40",
    highlightthickness=1,
    highlightbackground="#3a3a5a"
)
channel_wrapper.grid(row=0, column=0, padx=10, sticky="ew")

tk.Label(
    channel_wrapper,
    text="Channel Name",
    bg="#2a2a40",
    fg="#bbbbff",
    font=("Segoe UI", 9)
).pack(anchor="w", padx=12, pady=(8, 0))

channel_entry = tk.Entry(
    channel_wrapper,
    bg="#2a2a40",
    fg="white",
    insertbackground="white",
    relief="flat",
    font=("Segoe UI", 10)
)
channel_entry.pack(fill="x", padx=12, pady=(0, 10), ipady=6)


# Keyword Box
keyword_wrapper = tk.Frame(
    input_container,
    bg="#2a2a40",
    highlightthickness=1,
    highlightbackground="#3a3a5a"
)
keyword_wrapper.grid(row=0, column=1, padx=10, sticky="ew")

tk.Label(
    keyword_wrapper,
    text="Search Keyword",
    bg="#2a2a40",
    fg="#bbbbff",
    font=("Segoe UI", 9)
).pack(anchor="w", padx=12, pady=(8, 0))

keyword_entry = tk.Entry(
    keyword_wrapper,
    bg="#2a2a40",
    fg="white",
    insertbackground="white",
    relief="flat",
    font=("Segoe UI", 10)
)
keyword_entry.pack(fill="x", padx=12, pady=(0, 10), ipady=6)


# Search Button
ttk.Button(
    card,
    text="🔍 Search",
    command=start_search
).pack(pady=10)



# ---------- RESULTS FRAME (Resizable + Scrollbar) ----------
list_frame = tk.Frame(card, bg="#1e1e2f")
list_frame.pack(fill="both", expand=True, pady=10)

scrollbar = ttk.Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

results_listbox = tk.Listbox(
    list_frame,
    selectmode=tk.MULTIPLE,
    bg="#2a2a40",
    fg="white",
    selectbackground="#5757ff",
    yscrollcommand=scrollbar.set
)

results_listbox.pack(side="left", fill="both", expand=True)
scrollbar.config(command=results_listbox.yview)

ttk.Button(card, text="⬇ Download Selected",
           command=start_download).pack(pady=5)

# ---------- COUNT + PROGRESS + STATUS (SIDE BY SIDE) ----------

bottom_frame = tk.Frame(card, bg="#1e1e2f")
bottom_frame.pack(fill="x", padx=40, pady=15)

# Responsive columns
bottom_frame.columnconfigure(0, weight=1)  # Count
bottom_frame.columnconfigure(1, weight=3)  # Progress
bottom_frame.columnconfigure(2, weight=1)  # Status


# ---- Files Count Label ----
files_count_label = tk.Label(
    bottom_frame,
    text="📦 Total Files: 0",
    bg="#1e1e2f",
    fg="#00e5ff",
    font=("Segoe UI", 10, "bold")
)
files_count_label.grid(row=0, column=0, sticky="w")


# ---- Progress Bar ----
progress_bar = ttk.Progressbar(
    bottom_frame,
    mode="determinate"
)
progress_bar.grid(row=0, column=1, sticky="ew", padx=15, ipady=6)


# ---- Status Label ----
status_label = tk.Label(
    bottom_frame,
    text="Status: Idle",
    bg="#1e1e2f",
    fg="#00e5ff",
    font=("Segoe UI", 10, "bold")
)
status_label.grid(row=0, column=2, sticky="e")

root.mainloop()
