import sys
import json
import requests
from phe import paillier


def dec_to_bin(x):
    bin_vect = [0] * 12
    for i in range(12):
        bin_vect[i] = x & 1
        x >>= 1
    return bin_vect


def query_system(system_url, features, public_key, private_key, model):
    '''
    Send a query to one of the models
    input:  system_url - the url of the system
            features - features to encode and send
            public_key - public key used for encryption
            private_key - private key used for decoding the prediction
            model - model to query
    '''
    # Encrypt the feature vector
    enc_features = [public_key.encrypt(x).ciphertext() for x in features]

    # Assemble the message to submit
    data = {
        'email': email,
        'pk': public_key.n,
        'encrypted_input': enc_features,
        'model': model
    }
    # Submit the encrypted feature vector
    res = requests.post(system_url, json=data)
    if res.status_code != 200:
        print('Error occured when submitting the feature vector.')
        print('Status code', res.status_code)
        return -1

    # Decrypt the response
    enc_pred = paillier.EncryptedNumber(public_key, \
        json.loads(res.content)['encrypted_prediction'])
    pred = private_key.decrypt(enc_pred)

    return pred


def solve_first(system_url, email):
    '''
    Solve the first task, querying the first model
    input:  system_url - url to use for querying the system
            email - the email of the patient
    '''
    # URLs
    input_url = 'http://com402.epfl.ch/hw5/ex3/get_input'
    system_url = 'http://com402.epfl.ch/hw5/ex3/securehealth/prediction_service'
    token_url = 'http://com402.epfl.ch/hw5/ex3/get_token_1'

    # Get the input vector
    res = requests.post(input_url, json={'email': email})
    if res.status_code != 200:
        print('Error occured when requesting the input feature vector.')
        print('Status code', res.status_code)
        return
    features = json.loads(res.content)['x']

    # Generate key pair
    public_key, private_key = paillier.generate_paillier_keypair()

    # Get the prediction
    pred = query_system(system_url, features, public_key, private_key, 1)
    if pred == -1:
        return

    # Send the prediction and obtain the token
    data = {
        'email': email,
        'prediction': pred
    }
    res = requests.post(token_url, json=data)
    if res.status_code != 200:
        print('Error occured when submitting the prediction.')
        print('Status code', res.status_code)
        return

    # Print the token
    print(json.loads(res.content)['token'])


def solve_second(system_url, email):
    '''
    Solve the second task, querying the second model
    input:  system_url - url to use for querying the system
            email - the email of the patient
            model_check -
    '''
    token_url = 'http://com402.epfl.ch/hw5/ex3/get_token_2'

    # Generate key pair
    public_key, private_key = paillier.generate_paillier_keypair()

    # Find the bias
    features = [0] * 12
    bias = query_system(system_url, features, public_key, private_key, 2)
    if bias == -1:
        return

    # Find the weights one by one
    weights = [0] * 12
    for i in range(12):
        features = [0] * 12
        features[i] = 1
        weights[i] = query_system(system_url, features, public_key, \
            private_key, 2) - bias
        if weights[i] == -1:
            return

    # Submit the model parameters to get the token
    data = {
        'email': email,
        'weights': weights,
        'bias': bias
    }
    res = requests.post(token_url, json=data)
    if res.status_code != 200:
        print('Error occured when submitting the model parameters')
        print('Status code', res.status_code)
        print(res.content)
        return

    # Print the token
    print(json.loads(res.content)['token'])


if __name__ == '__main__':
    system_url = 'http://com402.epfl.ch/hw5/ex3/securehealth/prediction_service'
    email = 'alexandru.mocanu@epfl.ch'

    if len(sys.argv) < 2:
        print('Usage: python ex3.py TASK')
        sys.exit(1)

    task = int(sys.argv[1])
    if task == 1:
        solve_first(system_url, email)
    elif task == 2:
        solve_second(system_url, email)
