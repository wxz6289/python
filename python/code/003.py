from pprint import pprint
from random import shuffle

values = list(range(1, 11)) + "Jack Kueen King".split()
suits = "diamonds clubs heats spade".split()

deck = [f"{v} of {s}" for v in values for s in suits]

shuffle(deck)

part = deck[0:6]

while part: input(part.pop())
# pprint(deck)
# print(len(deck))
