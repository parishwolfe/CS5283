print("started", flush=True)
import socket
import utils
from utils import States

UDP_IP = "127.0.0.1"
UDP_IP = socket.gethostbyname(socket.gethostname())
UDP_PORT = 5005
print(UDP_IP, UDP_PORT, flush=True)

# initial server_state
server_state = States.CLOSED

sock = socket.socket(socket.AF_INET,    # Internet
                     socket.SOCK_DGRAM) # UDP

sock.bind((UDP_IP, UDP_PORT)) # wait for connection

# Some helper functions to keep the code clean and tidy
def update_server_state(new_state):
  global server_state
  if utils.DEBUG:
    print(server_state, '->', new_state, flush=True)
  server_state = new_state

# Receive a message and return header, body and addr
# addr is used to reply to the client
# this call is blocking
def recv_msg():
  data, addr = sock.recvfrom(1024)
  header = utils.bits_to_header(data)
  body = utils.get_body_from_data(data)
  return (header, body, addr)

# the server runs in an infinite loop and takes
# action based on current state and updates its state
# accordingly
# You will need to add more states, please update the possible
# states in utils.py file
while True:
  if server_state == States.CLOSED:
    # we already started listening, just update the state
    update_server_state(States.LISTEN)
  elif server_state == States.LISTEN:
    # we are waiting for a message
    header, body, addr = recv_msg()
    # if received message is a syn message, it's a connection
    # initiation
    if header.syn == 1:
      update_server_state(States.SYN_RECEIVED)
      seq_number = utils.rand_int() # we randomly pick a sequence number
      ack_number = header.seq_num + 1
      syn = header.syn + 1
      ack = header.ack + 1
      syn_ack_header = utils.Header(seq_number, ack_number, syn, ack)
      sock.sendto(syn_ack_header.bits(), addr)

      # to be implemented

      ### sending message from the server:
      #   use the following method to send messages back to client
      #   addr is recieved when we receive a message from a client (see above)
      #   sock.sendto(your_header_object.bits(), addr)

  elif server_state == States.SYN_RECEIVED:
    header, body, addr = recv_msg()
    print("received ack", flush=True)
    if header.ack_num == syn_ack_header.seq_num + 1 and header.seq_num == syn_ack_header.ack_num:
      update_server_state(States.ESTABLISHED)

  elif server_state == States.ESTABLISHED:
    header, body, addr = recv_msg()
    print("received_message", header, flush=True)
    # if header.fin != 1:
    #   # to be implemented, transfer data
    #   pass
    # elif header.fin == 1:
    if header:
      update_server_state(States.CLOSE_WAIT)
      fin_ack_header = utils.Header(utils.rand_int(), header.seq_num + 1, 0, 1)
      sock.sendto(fin_ack_header.bits(), addr)
      print("sent fin ack", flush=True)
      header, body, addr = recv_msg()
      print("head", header)
      if header.ack == 1 and fin_ack_header.seq_num + 1 == header.ack_num:
        update_server_state(States.CLOSED)


  else:
    pass
