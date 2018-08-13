import random, os, time
from nano25519.nano25519 import ed25519_oop as ed25519
from pyblake2 import blake2b
from bitstring import BitArray
import binascii
from configparser import SafeConfigParser
from modules import nano

def print_matrix(matrix):
    os.system('cls' if os.name == 'nt' else 'clear')
    line_num = 0
    print('#################')
    for x in reversed(matrix):
        print (x)
    print('#################')

def get_reply():
    while len(pending) > 0:
        rx_amount = nano.receive_xrb(int(index), account, wallet_seed)
        pending = nano.get_pending(str(account))
        print(len(pending))
        print('Rx amount %s' % rx_amount)

    return rx_amount

def wait_for_reply():
    while len(pending) == 0:
       pending = nano.get_pending(str(account))
       time.sleep(1)

# start game
print('Welcome to p2p Four in a Row on the Nano Network')
print('Please be aware that the internal seed is not encrypted so please be careful')
print()
print('Why have you made this?')
print('  Because...')
print()
print('Is this the low budget version of crypto kitties?')
print('  Yes')
print()
print('Can I make an interface that actually works?')
print('  Yes please')
print()

#setup board
board = [0,0,0,0,0,0,0,0,0,0]
w, h = 10, 10
board_matrix = [[' ' for x in range(w)] for y in range(h)]

parser = SafeConfigParser()
config_files = parser.read('config.ini')

if len(config_files) == 0:
    #Generate random seed
    print('Generate random seed')
    full_wallet_seed = hex(random.SystemRandom().getrandbits(256))
    wallet_seed = full_wallet_seed[2:].upper()

    cfgfile = open("config.ini",'w')
    parser.add_section('wallet')
    parser.set('wallet', 'seed', wallet_seed)
    parser.set('wallet', 'index', '0')
    index = 0

    parser.write(cfgfile)
    cfgfile.close()

else:
    print("Config file found")
    index = int(parser.get('wallet', 'index'))
    wallet_seed = parser.get('wallet', 'seed')

priv_key, pub_key = nano.seed_account(str(wallet_seed), 0)
public_key = str(binascii.hexlify(pub_key), 'ascii')

account = nano.account_xrb(str(public_key))
print("Account Address: ", account)

print("Please send 1 nano to this address")
print("Waiting for nano")

previous = nano.get_previous(str(account))
#print(previous)
#print(len(previous))
pending = nano.get_pending(str(account))

wait_for_reply()

pending = nano.get_pending(str(account))
if (len(previous) == 0) and (len(pending) > 0):
    print("Opening Account")
    nano.open_xrb(int(index), account, wallet_seed)

print("Rx Pending: ", pending)
pending = nano.get_pending(str(account))
print("Pending Len:" + str(len(pending)))

while len(pending) > 0:
    pending = nano.get_pending(str(account))
    print(len(pending))
    nano.receive_xrb(int(index), account, wallet_seed)

player = int(input("What player are you? (1 or 2): "))
target_account = input("Other players account address: ")

if player == 1:
    print()
    print('Sending empty board 0000000000')
    nano.send_xrb(target_account, 10000000000, account, 0, wallet_seed)
else:
    wait_for_reply()
    while len(pending) > 0:
        nano.receive_xrb(int(index), account, wallet_seed)
        pending = nano.get_pending(str(account))
        print(len(pending))

old_board = board.copy()

print('Waiting for other player move')
wait_for_reply()

rx_amount = "00000000000"
rx_amount = get_reply()

print(rx_amount)
old_board = board.copy()
board = list(rx_amount[-10:])

for position, char in enumerate(board):
     board[position] = int(char)    

print(board)

for x in range(len(old_board)):
    if board[x] == (int(old_board[x]) + 1):
        board_matrix[board[x]][x] = '0'
print_matrix(board_matrix)

while 1:
    #Your Move
    move = input('Which Column? ')
    if int(move) < 10:
        old_board = board.copy()
        board[int(move)] += 1
        print('You selected %d' % int(move))
    else:
        print('Error')
    #calculate difference and insert into matrix
    for x in range(len(old_board)):
        if board[x] == (int(old_board[x]) + 1):
            board_matrix[board[x]][x] = 'X'
    print_matrix(board_matrix)

    #send move via network
    board_amount = 0
    board_index = 0
    for x in board:
         board_amount = board_amount + (x * (10 ** board_index))
         board_index += 1

    print(board_amount)
    nano.send_xrb(target_account, (10000000000 + board_amount), account, 0, wallet_seed)

    #await reply
    old_board = board.copy()

    print('Waiting for reply')
    wait_for_reply()

    print('Found reply')

    rx_amount = get_reply()

    print(rx_amount)
    old_board = board.copy()
    board = list(rx_amount[-10:])

    for position, char in enumerate(board):
        board[position] = int(char)

    print(board)

    for x in range(len(old_board)):
        if board[x] == (int(old_board[x]) + 1):
            board_matrix[board[x]][x] = '0'
    print_matrix(board_matrix)

