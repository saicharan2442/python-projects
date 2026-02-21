'''import pyautogui
from datetime import datetime

# Generate filename with timestamp
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"screenshot_{timestamp}.png"

# Take screenshot
screenshot = pyautogui.screenshot()

# Save file
screenshot.save(filename)

print(f"Screenshot saved as {filename}")'''




'''

import tkinter as tk
import pyautogui
from datetime import datetime

def take_screenshot():
    status_label.config(text="Taking screenshot in 5 seconds...")
    root.update()
    
    # Wait 5 seconds
    root.after(5000, capture_screen)

def capture_screen():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"screenshot_{timestamp}.png"
    
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    
    status_label.config(text=f"Screenshot saved as {filename}")

# Create main window
root = tk.Tk()
root.title("Screenshot App")
root.geometry("300x150")

# Button
btn = tk.Button(root, text="Take Screenshot", command=take_screenshot, height=2, width=20)
btn.pack(pady=20)

# Status Label
status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()
'''





import tkinter as tk
import pyautogui
from datetime import datetime

def start_screenshot():
    root.withdraw()  # Hide main window
    show_countdown(5)

def show_countdown(count):
    overlay = tk.Toplevel()
    overlay.attributes("-fullscreen", True)
    overlay.attributes("-topmost", True)
    
    # Make background transparent (Windows)
    overlay.configure(bg="black")
    overlay.wm_attributes("-transparentcolor", "black")

    label = tk.Label(
        overlay,
        text=str(count),
        font=("Arial", 160, "bold"),
        fg="Light Blue",   # Change color if you want
        bg="black"
    )
    label.pack(expand=True)

    def update_countdown(c):
        if c > 0:
            label.config(text=str(c))
            overlay.after(1000, update_countdown, c - 1)
        else:
            overlay.destroy()
            capture_screen()

    update_countdown(count)

def capture_screen():
    # Flash animation
    flash = tk.Toplevel()
    flash.attributes("-fullscreen", True)
    flash.configure(bg="white")
    flash.attributes("-topmost", True)
    flash.attributes("-alpha", 0.7)
    flash.after(120, flash.destroy)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"screenshot_{timestamp}.png"

    screenshot = pyautogui.screenshot()
    screenshot.save(filename)

    root.deiconify()
    status_label.config(text=f"Screenshot saved as {filename}")

# Main window
root = tk.Tk()
root.title("Transparent Screenshot App")
root.geometry("350x200")

btn = tk.Button(root, text="Take Screenshot",
                command=start_screenshot,
                font=("Arial", 14),
                height=2, width=20)
btn.pack(pady=30)

status_label = tk.Label(root, text="", font=("Arial", 10))
status_label.pack()

root.mainloop()