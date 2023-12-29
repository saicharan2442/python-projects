# pip install phonenumbers

import phonenumbers
from phonenumbers import timezone, geocoder,carrier

# define a function to take argument
def mobileNumber(num):

    # Parsing String to Phone number
    number = phonenumbers.parse(num)

    # Validating a phone number
    valid_number = phonenumbers.is_valid_number(number)

    # Getting a time-zone information
    a = timezone.time_zones_for_number(number)
    print(a)

    # Getting carrier of a phone number
    b  = carrier.name_for_number(number, 'en')
    print(b)

    # Getting region information
    c = geocoder.description_for_number(number, 'en')
    print(c)
x=input("enter your number:")
# Calling a function with an argument -> Country code must be entered
num = mobileNumber("+91"+x)

