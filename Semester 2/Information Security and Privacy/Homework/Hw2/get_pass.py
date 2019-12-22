import sys
import base64


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

otp = "Never send a human to do a machine's job"

print(encrypt(sys.argv[1], otp))
