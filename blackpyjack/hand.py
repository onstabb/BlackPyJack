import copy
import enum
from dataclasses import dataclass, field

from card import Card, Rank

Hand = list[Card]


@enum.unique
class State(enum.Enum):
    WAIT = 0
    MOVING = enum.auto()
    ENOUGH = enum.auto()
    WIN = enum.auto()
    LOSE = enum.auto()
    PUSH = enum.auto()
    EVEN_MONEY = enum.auto()

    @classmethod
    def end_states(cls) -> tuple['State', 'State', 'State', 'State']:
        return cls.WIN, cls.LOSE, cls.PUSH, cls.EVEN_MONEY,


@dataclass
class BlackJackHand:
    cards: Hand = field(default_factory=list)
    bet: int = 0
    state: State = State.WAIT


def reset(hand: BlackJackHand) -> None:
    hand.cards.clear()
    hand.bet = 0
    hand.state = State.WAIT


def give_out_last_cards(from_hand: BlackJackHand, to_hand: BlackJackHand, count: int = 1) -> None:
    for _ in range(count):
        card: Card = from_hand.cards.pop()
        to_hand.cards.append(card)


def get_score(hand: BlackJackHand) -> int:
    score: int = 0
    contains_ace: bool = False
    for card in hand.cards:
        card_value: int = min(10, card.rank.value)
        score += card_value
        if card.rank == Rank.ACE:
            contains_ace = True

    if contains_ace and score <= 11:
        score += 10

    return score


def is_busted(hand: BlackJackHand) -> bool:
    return get_score(hand) > 21
