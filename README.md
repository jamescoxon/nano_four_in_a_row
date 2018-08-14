# nano\_four\_in\_a\_row

Fun game of Four In A Row coded in python. All moves are transmitted using [NANO](https://nano.org/) transactions.

## Installation

`git clone https://github.com/jamescoxon/nano_four_in_a_row --recursive`

```bash
cd nano_four_in_a_row
sudo apt-get install python3-pip
pip3 install -r requirements.txt
```

## Play

`python3 play.py`

Get a second player and perform the following steps:

1.  Take note of the account address that the game gives you.
2.  Send 0.000001 nano to that account (**NOTE**: you only need to do this once, not for every game!). The QRcode already has the correct amount if you scan it with a phone wallet.
3.  Choose player 1/2 (if you're player 1, you should wait until player 2 has started the game)
4.  Paste the account that your opponent gives you, and give him yours
5.  Wait for the game's instructions
6.  Have fun!
