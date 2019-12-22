import base64
from flask import Flask, Response, request


# Initialize Flask app
app = Flask(__name__)

def encrypt(msg, key):
    '''
    Encrypt message using one time pad key
    input:  msg - message to be encrypted
            key - one time pad key
    output: password
    '''
    while len(key) < len(msg):
        # Increase the length of the key
        diff = len(msg) - len(key)
        key += key[:diff]

    # Get the ascii representations of the message and the key
    amsg = list(map(lambda x: ord(x), list(msg)))
    akey = list(map(lambda x: ord(x), list(key[:len(msg)])))
    # XOR the message and the key
    xor = list(map(lambda x, y: x ^ y, amsg, akey))
    # Transform ascii encrypted message into string
    pwd = ''.join(list(map(lambda x: chr(x), xor)))
    # Encode password inn base64
    pwd = base64.b64encode(pwd.encode())

    return pwd.decode()


def check_pass(user, pwd):
    '''
    Return an appropriate status according to the password corresponding to the
    user or not
    input:  user - username
            pwd - password
    '''
    MAX_LEN = 100
    otp = "Never send a human to do a machine's job"
    # Check the user and pass have normal lengths
    if len(user) > MAX_LEN or len(pwd) > MAX_LEN:
        return Response("Wrong user or password length", status=400)
    # Get expected password
    enc = encrypt(user, otp)
    # Check if the password corresponds to the user
    if enc == pwd:
        return Response("Logged in", status=200)
    return Response("Wrong password", status=400)


def do_login():
    '''
    Get username and password and process them to do the login
    '''
    json = request.get_json()
    # Terminate if we don't find the user and pass
    if json is None or 'user' not in json or 'pass' not in json:
        return Response("User or pass was not provided", status=400)
    # Get user and pass
    user = json['user']
    pwd = json['pass']
    # Check the credentials
    return check_pass(user, pwd)


# Bind function to webpage
@app.route('/hw2/ex1', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        return do_login()
    else:
        return 'Hello there!'

app.run()
