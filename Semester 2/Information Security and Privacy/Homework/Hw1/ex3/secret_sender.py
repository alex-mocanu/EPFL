import requests


# List of secrets
secrets = ['9511.5627.6664.0851',
'6009/7169/9461/0356',
'4411/2529/6598/0520',
'L2JRR5QC2L7X6',
'2OYLN>K2WU79H=']

# Set destination of the http post request and the data to send
destination = 'http://com402.epfl.ch/hw1/ex4/sensitive'
data = {
    'student_email': 'alexandru.mocanu@epfl.ch',
    'secrets': secrets
}

# Send data
requests.post(destination, json=data)
