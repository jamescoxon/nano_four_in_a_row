#!/usr/bin/env python3

import random, os, time, sys
from nano25519.nano25519 import ed25519_oop as ed25519
from pyblake2 import blake2b
from bitstring import BitArray
import binascii
from configparser import SafeConfigParser
from modules import nano
import pyqrcode

BOARDWIDTH = 10
BOARDHEIGHT = 10
RAW_AMOUNT = 1000000000000000000000000 # 1e24

def print_matrix(matrix):
    os.system('cls' if os.name == 'nt' else 'clear')
    line_num = 0
    print('##################################################')
    for x in range(0,10):
        matrix[0][x] = '%s' % x

    for x in reversed(matrix):
        print (x)
    print('##################################################')

def get_reply(account, index, wallet_seed):
    pending = nano.get_pending(str(account))
    while len(pending) > 0:
        rx_amount = nano.receive_xrb(int(index), account, wallet_seed)
        pending = nano.get_pending(str(account))
        print(len(pending))
        print('Rx amount %s' % rx_amount)

    return rx_amount

def wait_for_reply(account, with_plot=None):
    pending = nano.get_pending(str(account))
    while len(pending) == 0:
       pending = nano.get_pending(str(account))
       time.sleep(2)
       print('.', end='', flush=True)
       if with_plot is not None:
           with_plot.pause(0.001)
    print()

# From http://inventwithpython.com/extra/fourinarow_text.py
# Four-In-A-Row (a Connect Four clone)
# http://inventwithpython.com/blog
# By Al Sweigart al@inventwithpython.com

def isWinner(board, tile):
    # check horizontal spaces
    for y in range(BOARDHEIGHT):
        for x in range(BOARDWIDTH - 3):
            if board[x][y] == tile and board[x+1][y] == tile and board[x+2][y] == tile and board[x+3][y] == tile:
                return True

    # check vertical spaces
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT - 3):
            if board[x][y] == tile and board[x][y+1] == tile and board[x][y+2] == tile and board[x][y+3] == tile:
                return True

    # check / diagonal spaces
    for x in range(BOARDWIDTH - 3):
        for y in range(3, BOARDHEIGHT):
            if board[x][y] == tile and board[x+1][y-1] == tile and board[x+2][y-2] == tile and board[x+3][y-3] == tile:
                return True

    # check \ diagonal spaces
    for x in range(BOARDWIDTH - 3):
        for y in range(BOARDHEIGHT - 3):
            if board[x][y] == tile and board[x+1][y+1] == tile and board[x+2][y+2] == tile and board[x+3][y+3] == tile:
                return True

    return False

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
board_matrix = [[' ' for x in range(BOARDWIDTH)] for y in range(BOARDHEIGHT)]

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

previous = nano.get_previous(str(account))
pending = nano.get_pending(str(account))
#print(previous)
if (len(previous) == 0) and (len(pending) == 0):

    print("Please send 0.000001 nano to this address")
    try:
        import matplotlib.image as mpimg
        import matplotlib.pyplot as plt
        # qr code gen
        uri = "xrb:{account}?amount={raw}&label=Four%20In%20A%20Row&message=Thank%20you%20for%20playing&my&game!".format(account=account, raw=RAW_AMOUNT)
        code = pyqrcode.create(uri, encoding='iso-8859-1')

        # display with tkinter (not working on macOS)
        #code_xbm = code.xbm(scale=7, quiet_zone=5)
        #top = tkinter.Tk()
        #code_bmp = tkinter.BitmapImage(data=code_xbm)
        #code_bmp.config(background="white")
        #label = tkinter.Label(image=code_bmp)
        #label.pack()

        # display with matplotlip
        code.eps('qrcode.eps', scale=5, quiet_zone=7)
        code_eps = mpimg.imread('qrcode.eps')
        imgplot = plt.imshow(code_eps)
        plt.ion()
        plt.show()
        plt.pause(0.001)
    except Exception as e:
        print(e)
        data = 'xrb:' + account
        xrb_qr = pyqrcode.create(data, encoding='iso-8859-1')
        print(xrb_qr.terminal())

    print('Waiting for nano to arrive at {}'.format(account))
    wait_for_reply(account, with_plot=plt)
else:
    print('You already have enough balance, great!')

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
    print('\nSending empty board 0000000000')
    nano.send_xrb(target_account, 10000000000, account, 0, wallet_seed)
else:
    print("\nWaiting for Player 1 to start the game")
    wait_for_reply(account)
    while len(pending) > 0:
        nano.receive_xrb(int(index), account, wallet_seed)
        pending = nano.get_pending(str(account))
        print(len(pending))

old_board = board.copy()

print('Waiting for other player move')
wait_for_reply(account)

rx_amount = "00000000000"
rx_amount = get_reply(account, index, wallet_seed)

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
    move = ''
    while move == '':
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
    print('Sending to other player with a nano transaction')
    nano.send_xrb(target_account, (10000000000 + board_amount), account, 0, wallet_seed)

    if isWinner(board_matrix, 'X') == True:
        print("You (X) are the winner")
        sys.exit()

    #await reply
    old_board = board.copy()

    print('Waiting for reply')
    wait_for_reply(account)

    print('Found reply')

    rx_amount = get_reply(account, index, wallet_seed)

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
    if isWinner(board_matrix, '0') == True:
        print("They (0) are the winner")
        sys.exit()

