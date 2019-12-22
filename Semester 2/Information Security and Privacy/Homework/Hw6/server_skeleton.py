#!/usr/bin/env python3

import sys
import socket
import threading
import binascii

PRIMARY_SERVER_ID = 0

CHAT_MSG_INDEX_SIZE = 20
CHAT_MSG_BODY_SIZE  = 44

class PIRServer:

    # Server id - determines the order servers
    server_id = None

    server_ip   = None
    udp_port    = None
    udp_socket  = None

    # Dictionary of all servers, key is server_id and value is (ip, port) pair
    all_servers = None

    chat_messages = None

    def __init__(self, server_id, server_ip, udp_port, all_servers):

        self.server_id    = server_id
        self.server_ip    = server_ip
        self.udp_port     = udp_port
        self.all_servers  = all_servers

        self.udp_socket   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((server_ip, udp_port))
        self.udp_socket.settimeout(10)

        self.chat_messages = dict()


    # Receive a chat message from the client, only the primary server
    # should receive this message. The message is a string.
    def recv_chat_msg_client(self, msg):

        # Only primary server should receive/process
        # a chat message from a client
        if self.server_id != PRIMARY_SERVER_ID:
            return

        # Store the message
        # TODO: insert your code here!
        # If there is next server send the message to it

        next_server_id = self.server_id + 1
        if next_server_id in self.all_servers.keys():
            # TODO: insert your code here!
            pass

    # Receive a chat message from another server (the previous server in the chain)
    def recv_chat_msg_server(self, msg, sender):

        # Check if the message is sent by the previous server in the chain
        # If not, ignore the messsage
        # TODO: insert your code here!

        # Store the message
        # TODO: insert your code here!
        # If there is next server send the message to it

        next_server_id = self.server_id + 1
        if next_server_id in self.all_servers.keys():

            # TODO: insert your code here!
            pass


    # Process the PIR request from a client. Bitmask has _n_ bits,
    # where _n_ is the number of chat messages. Each bit _j_ in the bitmask
    # corresponds to the chat message with index _j_. If _j_ is set to 1,
    # the message with this index is 'selected'.
    # Xor all messages selected by the bitmask and send the result back
    def process_pir_request(self, bitmask, sender):

        result = b''

        # TODO: insert your code here!

        # Please be careful here, our client expects the result as bytes
        # type(result) = <class 'bytes'> in Python3
        self.udp_socket.sendto(result, sender)



    # Method which runs in a thread
    def run(self):

        print('Server', self.server_id, 'starting...')

        while(True):

            # Server will listen on the assigned port and wait for a message
            # If no message is received for more than the timeout time,
            # which is set in the init method, exception will be raised,
            # and thread will stop.
            try:
                message, sender = self.udp_socket.recvfrom(4096)
            except socket.timeout:
                print('Server %d udp-receive timedout' % self.server_id)
                break

            # Received message is of type bytes, so we decode it to get string
            message = message.decode('utf-8')
            print("message is", message)

            op_code = message.split()[0]
            print('Server', self.server_id, 'received op_code:', op_code)


            if op_code == 'chat_msg_client':
                # Client sends a chat message
                chat_msg = message.split(' ', 1)[1]
                self.recv_chat_msg_client(chat_msg)

            elif op_code == 'chat_msg_server':
                # Previous server sends a chat message
                chat_msg = message.split(' ', 1)[1]
                self.recv_chat_msg_server(chat_msg, sender)


            elif op_code == 'pir_req':
                # Client sends PIR request
                bitmask = int(message.split(' ', 1)[1])
                self.process_pir_request(bitmask, sender)

            elif op_code == 'quit':
                print('Server', self.server_id, 'quiting...')
                break

            else:
                err_msg = 'Op_code %s not supported' % op_code
                self.udp_socket.sendto(err_msg.encode(), sender)


def read_server_data():

    # Read data about the servers from a file
    servers_filename = 'all_servers.txt'

    all_servers = dict()
    with open(servers_filename, 'r') as fp:

        for line in fp.readlines():
            server_id = int(line.split()[0])
            server_ip = line.split()[1]
            udp_port  = int(line.split()[2])

            all_servers[server_id] = (server_ip, udp_port)

    return all_servers


def main():

    all_servers = read_server_data()

    # Create PIRServers and run each one in a separate thread
    server_threads = []
    for server_id, (server_ip, udp_port) in all_servers.items():

        ser = PIRServer(server_id, server_ip, udp_port, all_servers)
        server_threads.append(threading.Thread(target=ser.run))
        server_threads[-1].start()

    for thr in server_threads:
        thr.join()


if __name__ == '__main__':
    main()
