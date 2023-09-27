from dataclasses import dataclass
from enum import Enum, auto, unique


@unique
class Suit(Enum):
    CLUBS = 0
    DIAMONDS = auto()
    HEARTS = auto()
    SPADES = auto()


@unique
class Rank(Enum):
    ACE = auto()
    TWO = auto()
    THREE = auto()
    FOUR = auto()
    FIVE = auto()
    SIX = auto()
    SEVEN = auto()
    EIGHT = auto()
    NINE = auto()
    TEN = auto()
    JACK = auto()
    QUEEN = auto()
    KING = auto()


@dataclass(frozen=True, slots=True)
class Card:
    rank: Rank
    suit: Suit
