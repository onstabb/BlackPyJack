import pytest

from card import Card, Rank, Suit
from hand import get_score, BlackJackHand


hands_and_expected_scores = [
    (
        [
            Card(rank=Rank.KING, suit=Suit.HEARTS),
            Card(rank=Rank.FIVE, suit=Suit.SPADES),
        ],
        15
    ),
    (
        [
            Card(rank=Rank.TEN, suit=Suit.DIAMONDS),
            Card(rank=Rank.ACE, suit=Suit.HEARTS),
        ],
        21
    ),
    (
        [
            Card(rank=Rank.NINE, suit=Suit.CLUBS),
            Card(rank=Rank.SEVEN, suit=Suit.DIAMONDS),
        ],
        16
    ),
    (
        [
            Card(rank=Rank.FOUR, suit=Suit.SPADES),
            Card(rank=Rank.JACK, suit=Suit.CLUBS),
            Card(rank=Rank.QUEEN, suit=Suit.HEARTS),
        ],
        24
    ),
    (
        [
            Card(rank=Rank.ACE, suit=Suit.SPADES),
            Card(rank=Rank.TEN, suit=Suit.CLUBS),
            Card(rank=Rank.FIVE, suit=Suit.HEARTS),
        ],
        16
    ),
]


@pytest.mark.parametrize("hand, score", hands_and_expected_scores)
def test_get_score(hand, score):
    assert get_score(BlackJackHand(cards=hand)) == score
