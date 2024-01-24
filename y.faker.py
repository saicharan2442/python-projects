# run it in jupyter lab

#pip install faker

from faker import Faker
f=Faker()

# fake profiles 
print("profile :",f.profile())

print("\n\n\n\n\n\n")

# fake IP address 
from faker.providers import internet
print("fake IP address :", f.ipv4_private())

# fake name
print("fake name :",f.name())
                       
#fake Address
print("fake address :",f.address())

# fake credit card details
print("fake credit card full :", f.credit_card_full())

# fake email
print("fake email :", f.email())

#fake url
print("fake url :", f.url())

# fake licence plate
print("fake licence plate :", f.license_plate())

#fake currency
print("fake currency :", f.currency())

#fake colorname
print("fake color name :", f.color_name())

# fake latitude & langitude
print("fake latitude & langitude :", f.local_latlng())

#fake domine name
print("fake domine name :", f.domain_name())

#fake company
print("company :", f.company())

#fake sentence
print("fake sentence :",f.sentence())

#fake text
print("text :", f.text())

