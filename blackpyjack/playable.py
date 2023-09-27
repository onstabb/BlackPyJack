import abc
import enum
from dataclasses import field, dataclass

import hand
from card import Rank
from hand import BlackJackHand


@enum.unique
class Move(enum.Enum):
    NONE = 0
    HIT = enum.auto()
    STAND = enum.auto()
    DOUBLE = enum.auto()
    SPLIT = enum.auto()
    INSURANCE = enum.auto()
    EVEN_MONEY = enum.auto()


@dataclass
class BaseBlackJackPlayable(abc.ABC):
    name: str
    chips: int = 0
    move: Move = Move.NONE
    is_bot: bool = False


@dataclass
class BlackJackPlayer(BaseBlackJackPlayable):
    hands: list[BlackJackHand] = field(default_factory=list)
    insurance: int = 0


@dataclass
class Dealer(BaseBlackJackPlayable):
    hand: BlackJackHand = field(default_factory=BlackJackHand)


def make_move(playable: BaseBlackJackPlayable) -> Move:
    move: Move = playable.move
    playable.move = Move.NONE
    return move


# Player functions --------------------------------------------------------------------------------------------
def reset_hands(player: BlackJackPlayer) -> None:
    player.hands.clear()
    player.hands.append(BlackJackHand())
    player.insurance = 0


def get_current_hand(player: BlackJackPlayer) -> hand.BlackJackHand:
    wait_hand: hand.BlackJackHand | None = None

    for player_hand in player.hands:
        if player_hand.state == hand.State.MOVING:
            return player_hand
        if player_hand.state == hand.State.WAIT and not wait_hand:
            wait_hand = player_hand

    if wait_hand:
        return wait_hand

    return player.hands[0]


def apply_insurance(player: BlackJackPlayer) -> None:
    if player.hands[0].bet == 0:
        raise ValueError("No placed bet")

    player.insurance = player.hands[0].bet
    player.chips -= player.insurance // 2


def place_bet(player: BlackJackPlayer, bet: int, player_hand: hand.BlackJackHand) -> None:

    if hand not in player.hands:
        raise AttributeError("This hand does not belong to this player")

    player.chips -= bet
    player_hand.bet += bet


def reset_bet(player: BlackJackPlayer, player_hand: hand.BlackJackHand) -> None:

    if hand not in player.hands:
        raise AttributeError("This hand does not belong to this player")

    player.chips += player_hand.bet
    player_hand.bet = 0


def split(player: BlackJackPlayer) -> None:
    new_hand: hand.BlackJackHand = hand.BlackJackHand()
    current_active_hand: hand.BlackJackHand = get_current_hand(player=player)
    hand.give_out_last_cards(current_active_hand, new_hand, count=1)
    new_hand.bet = current_active_hand.bet
    player.chips -= new_hand.bet
    player.hands.append(new_hand)


def can_get_insurance(player: BlackJackPlayer, dealer: Dealer) -> bool:
    if not get_current_hand(player) != hand.State.MOVING:
        return False

    if player.insurance:
        return False

    if dealer.hand.cards[0].rank != Rank.ACE:
        return False

    if player.chips - (player.hands[0].bet // 2) < 0:
        return False

    if can_even_money(player, dealer):
        return False

    return True


def can_double(player: BlackJackPlayer) -> bool:
    player_hand: hand.BlackJackHand = get_current_hand(player)

    if not player_hand:
        return False

    if player.chips - player_hand.bet < 0:
        return False

    if len(player_hand.cards) == 2:
        return True

    return False


def can_split(player: BlackJackPlayer, max_splits: int = 1) -> bool:

    player_hand = get_current_hand(player)

    if not can_double(player):
        return False

    if len(player.hands) > max_splits:
        return False

    if player_hand.cards[0].rank != player_hand.cards[1].rank:
        return False

    return True


def can_even_money(player: BlackJackPlayer, dealer: Dealer) -> bool:

    player_hand = get_current_hand(player)

    if not player_hand.state != hand.State.MOVING:
        return False

    if hand.get_score(player_hand) != 21:
        return False

    if dealer.hand.cards[0].rank != Rank.ACE:
        return False

    if player.insurance:
        return False

    return True


# Dealer functions --------------------------------------------------------------------------------------------
def get_dealer_move(dealer: Dealer) -> Move:
    if hand.get_score(dealer.hand) < 17:
        return Move.HIT
    return Move.STAND


def give_chips(from_player: BaseBlackJackPlayable, to_player: BaseBlackJackPlayable, chips: int) -> None:
    from_player.chips -= chips
    to_player.chips += chips


def reset_hand(dealer: Dealer) -> None:
    hand.reset(dealer.hand)
