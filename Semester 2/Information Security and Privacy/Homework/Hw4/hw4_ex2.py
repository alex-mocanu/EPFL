import bcrypt
from flask import Flask, Response, request


# Initialize Flask app
app = Flask(__name__)


# Bind function to webpage
@app.route('/hw4/ex2', methods=['POST'])
def main():
    # Get request data
    json = request.get_json()
    # Terminate if we don't find the user and pass
    if json is None or 'user' not in json or 'pass' not in json:
        return Response("User or pass was not provided", status=400)
    # Obtain the password hash
    pw_hash = bcrypt.hashpw(json['pass'].encode(), bcrypt.gensalt())
    return Response(pw_hash, status=200)


app.run()
