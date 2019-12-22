import hmac
import time
import base64
from flask import Flask, Response, make_response, request


hmac_key = 'LwkTHRNOFxcbSk0OQwkbGCELUBIDDgcH'.encode()
cookie_name = 'LoginCookie'

# Initialize Flask app
app = Flask(__name__)


def serve_cookie(user, pwd):
    '''
    Serve a cookie to a user given its password
    input:  user - username
            pwd - password
    ouput:  response containing cookie
    '''
    cookie_type = 'user'
    if user == 'administrator' and pwd == '42':
        cookie_type = 'administrator'
    # Create cookie content
    content = ','.join([user, str(int(time.time())), 'com402', 'hw2', 'ex3', \
        cookie_type])
    # Create hmac
    h = hmac.new(hmac_key)
    h.update(content.encode())
    hex_hmac = h.hexdigest()
    # Append hmac to content
    content += ',' + hex_hmac
    content = base64.b64encode(content.encode()).decode()
    # Generate response
    resp = make_response()
    resp.set_cookie(cookie_name, content)

    return resp


def do_login():
    '''
    Get username and password and process them to serve a cookie
    '''
    json = request.get_json()
    # Terminate if we don't find the user and pass
    if json is None or 'user' not in json or 'pass' not in json:
        return Response("User or pass was not provided", status=400)
    # Get user and pass
    user = json['user']
    pwd = json['pass']
    # Serve cookie
    return serve_cookie(user, pwd)


def check_access():
    '''
    Once the cookie was transmitted, provide access according to the user's
    privileges
    '''
    # Get cookie
    raw_content = request.cookies.get(cookie_name)
    content = base64.b64decode(raw_content.encode()).decode().split(',')
    curr_hmac = content[-1]
    cookie_type = content[-2]
    simple_content = ','.join(content[:-1])
    # Check HMAC
    h = hmac.new(hmac_key)
    h.update(simple_content.encode())
    true_hmac = h.hexdigest()
    if true_hmac != curr_hmac:
        return Response("So you're a wise guy", status=403)
    elif cookie_type == 'user':
        return Response("Welcome peasant", status=201)
    else:
        return Response("Long live the admin", status=200)


# Bind function to webpage
@app.route('/ex3/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return do_login()
    else:
        return 'Hello there!'

# Bind function to webpage
@app.route('/ex3/list', methods=['GET', 'POST'])
def access():
    if request.method == 'POST':
        return check_access()
    else:
        return 'Hello there!'

app.run()