import pyautogui
import time
import random

IDLE_TIME = 30  # 2 minutes
CHECK_INTERVAL = 1

screen_w, screen_h = pyautogui.size()

last_user_pos = pyautogui.position()
last_activity_time = time.time()

auto_mode = False

print("Mouse activity watcher started...")

while True:

    current_pos = pyautogui.position()

    # Detect manual movement while idle
    if not auto_mode and current_pos != last_user_pos:
        last_user_pos = current_pos
        last_activity_time = time.time()

    # Start auto mode after 2 minutes
    if not auto_mode and (time.time() - last_activity_time >= IDLE_TIME):
        print("Idle detected → starting continuous movement")
        auto_mode = True

    # AUTO MOVEMENT LOOP
    while auto_mode:

        start_pos = pyautogui.position()

        # move to random place on screen
        new_x = random.randint(0, screen_w)
        new_y = random.randint(0, screen_h)

        pyautogui.moveTo(new_x, new_y, duration=random.uniform(0.5, 1.5))

        time.sleep(random.uniform(0.3, 1))

        # if mouse moved somewhere unexpected -> user moved it
        if pyautogui.position() != (new_x, new_y):
            print("Manual movement detected → stopping auto mode")
            auto_mode = False
            last_user_pos = pyautogui.position()
            last_activity_time = time.time()
            break

    time.sleep(CHECK_INTERVAL)