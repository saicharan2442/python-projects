import os
def shutdown_PC():
    os.system("shutdown /s /t 1")
shutdown_PC()



# ---------------Another Version based on user input--------------------#


import os

def shutdown_pc():
    try:
        # Ask user for time in seconds
        time_seconds = int(input("Enter shutdown time in seconds: "))

        if time_seconds < 0:
            print("❌ Time cannot be negative")
            return

        # Execute shutdown command
        os.system(f"shutdown /s /t {time_seconds}")
        print(f"⚠️ PC will shut down in {time_seconds} seconds")

    except ValueError:
        print("❌ Please enter a valid number")

shutdown_pc()
