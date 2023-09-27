
from typing import TYPE_CHECKING

from card import Card, Suit, Rank

if TYPE_CHECKING:
    from hand import BlackJackHand

Deck = list[Card]


def populate(deck: Deck, count: int):
    for _ in range(count):
        for suit in Suit:
            for rank in Rank:
                new_card: Card = Card(rank, suit)
                deck.append(new_card)


def hand_out_last_cards(from_deck: Deck, to_hand: BlackJackHand, count: int = 1) -> None:
    for _ in range(count):
        card: Card = from_deck.pop()
        to_hand.cards.append(card)
