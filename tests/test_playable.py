
import pytest

import hand
import playable
from card import Card, Rank, Suit


@pytest.mark.parametrize(
    "player_hand",
    [
        [
            hand.BlackJackHand(state=hand.State.ENOUGH, bet=3),
            hand.BlackJackHand(state=hand.State.ENOUGH, bet=1),
            hand.BlackJackHand(state=hand.State.MOVING, bet=11),
        ],
        [
            hand.BlackJackHand(state=hand.State.ENOUGH, bet=11),
            hand.BlackJackHand(state=hand.State.ENOUGH, bet=1),
            hand.BlackJackHand(state=hand.State.ENOUGH, bet=3),
        ],
    ]
)
def test_get_current_hand(player_hand):
    player = playable.BlackJackPlayer(name="Test", hands=player_hand)
    assert playable.get_current_hand(player).bet == 11


@pytest.mark.parametrize(
    "player_chips, player_bet, dealer_hand, expected_insurance, expected_chips",
    [
        (200, 100, [Card(Rank.ACE, Suit.HEARTS)], 100, 150),
        (500, 100, [Card(Rank.ACE, Suit.CLUBS)], 100, 450),
    ],
)
def test_apply_insurance(player_chips, player_bet, dealer_hand, expected_insurance, expected_chips):
    player = playable.BlackJackPlayer(name="Test", chips=player_chips)
    player.hands.append(
        hand.BlackJackHand(state=hand.State.MOVING, bet=player_bet, cards=[Card(Rank.JACK, Suit.CLUBS)])
    )
    dealer = playable.Dealer("dealer" )
    dealer.hand.cards = dealer_hand

    assert playable.can_get_insurance(player, dealer)
    playable.apply_insurance(player)

    assert player.insurance == expected_insurance
    assert player.chips == expected_chips
