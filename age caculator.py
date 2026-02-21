'''
y=int(input("enter year:"))
def ageCalculator(y, m, d):
    import datetime
    today = datetime.datetime.now().date()
    dob = datetime.date(y, m, d)
    age = int((today-dob).days / 365.25)
    print(age)
ageCalculator(y,1,1)
'''
# Another Approach--------------------------------------------------------

import datetime
import time
import sys

def age_calculator(year, month, day, hour=0, minute=0, second=0):
    dob = datetime.datetime(year, month, day, hour, minute, second)

    print("\n🎂 LIVE AGE CALCULATOR")
    print("-" * 40)

    while True:
        now = datetime.datetime.now()

        if now < dob:
            print("Birth date is in the future!")
            break

        # Year, Month, Day calculation
        years = now.year - dob.year
        months = now.month - dob.month
        days = now.day - dob.day

        if now.day < dob.day:
            months -= 1
            prev_month = now.month - 1 if now.month > 1 else 12
            prev_year = now.year if now.month > 1 else now.year - 1
            days_in_prev_month = (
                datetime.datetime(prev_year, prev_month % 12 + 1, 1)
                - datetime.timedelta(days=1)
            ).day
            days += days_in_prev_month

        if months < 0:
            years -= 1
            months += 12

        # Total time difference
        total_diff = now - dob
        total_seconds = int(total_diff.total_seconds())

        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds // 60) % 60
        seconds = total_seconds % 60

        output = (
            f"\rYears: {years} | "
            f"Months: {months} | "
            f"Days: {days} | "
            f"Time: {hours:02}:{minutes:02}:{seconds:02}"
        )

        sys.stdout.write(output)
        sys.stdout.flush()

        time.sleep(1)


# -------------------------
# User Input
# -------------------------

y = int(input("Enter birth year  : "))
m = int(input("Enter birth month : "))
d = int(input("Enter birth day   : "))

birth_time = input("Enter birth time (HH:MM:SS) [Optional] : ")

if birth_time.strip() == "":
    h, mi, s = 0, 0, 0
else:
    try:
        h, mi, s = map(int, birth_time.split(":"))
    except:
        print("Invalid format! Using 00:00:00")
        h, mi, s = 0, 0, 0

age_calculator(y, m, d, h, mi, s)


