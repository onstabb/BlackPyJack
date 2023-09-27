from random import Random, randint

from deck import Deck

SEED = randint(-10000, 100000)
rand = Random()


def shuffle(deck: Deck, rand_state: tuple) -> tuple:
    rand.setstate(rand_state)
    rand.shuffle(deck)
    return rand.getstate()



