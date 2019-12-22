import os
import asyncio
import hashlib
import binascii
import websockets


# Parameters
websock = 'ws://com402.epfl.ch/hw2/ws'
user = 'cosmin.rusu@epfl.ch'
pwd = 'LQoFCBtOXRcbF1UhRRgTAU8NSA=='
N = "EEAF0AB9ADB38DD69C33F80AFA8FC5E86072618775FF3C0B9EA2314C9C256576D674DF7496EA81D3383B4813D692C6E0E0D5D8E250B98BE48E495C1D6089DAD15DC7D7B46154D6B6CE8EF4AD69B15D4982559B297BCF1885C529F566660E57EC68EDBC3C05726CC02FD4CBF4976EAA9AFD5138FE8376435B9FC61D2FC0EB06E3"
g = 2


async def main(websock, user, pwd, N, g):
    async with websockets.connect(websock) as websocket:
        N = int.from_bytes(binascii.unhexlify(N), 'big')

        # Send username
        await websocket.send(user.encode())

        # Receive and decode salt
        salt = await websocket.recv()

        # Generate A
        raw_a = binascii.b2a_hex(os.urandom(16))
        a = int.from_bytes(binascii.unhexlify(raw_a), 'big')
        A = pow(g, a, N)

        # Send A
        buffA = A.to_bytes((A.bit_length() + 7) // 8, 'big')
        aToSend = binascii.hexlify(buffA).decode()
        await websocket.send(aToSend)

        # Receive B
        raw_B = await websocket.recv()
        B = int.from_bytes(binascii.unhexlify(raw_B), 'big')
        buffB = B.to_bytes((B.bit_length() + 7) // 8, 'big')

        # Get hash of A and B
        sha256 = hashlib.sha256()
        sha256.update(binascii.unhexlify(aToSend))
        sha256.update(binascii.unhexlify(raw_B))
        raw_u = sha256.hexdigest()
        u = int.from_bytes(binascii.unhexlify(raw_u), 'big')

        # Hash user and password
        sha256 = hashlib.sha256()
        sha256.update(user.encode())
        sha256.update(':'.encode())
        sha256.update(pwd.encode())
        aux_hash = sha256.digest()
        # Get x
        sha256 = hashlib.sha256()
        sha256.update(binascii.unhexlify(salt))
        sha256.update(aux_hash)
        raw_x = sha256.hexdigest()
        x = int.from_bytes(binascii.unhexlify(raw_x), 'big')

        # Compute the secret key
        S = pow(B - pow(g, x, N), a + u * x, N)

        # Send final message
        sha256 = hashlib.sha256()
        sha256.update(binascii.unhexlify(aToSend))
        sha256.update(binascii.unhexlify(raw_B))
        sha256.update(S.to_bytes((S.bit_length() + 7) // 8, 'big'))
        final_msg = sha256.digest()
        await websocket.send(binascii.hexlify(final_msg).decode())

        # Receive token
        token = await websocket.recv()
        print(token)


asyncio.get_event_loop().run_until_complete(main(websock, user, pwd, N, g))
