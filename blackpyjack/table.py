from dataclasses import dataclass, field


import deck as decks
import exceptions
import hand
import playable
import rand

from events import Events


@dataclass
class TableConfig:
    RAND_STATE: tuple = rand.rand.getstate()
    DECKS_COUNT: int = 2
    MAX_SPLITS: int = 1
    REMAINING_CARDS_FOR_SHUFFLING: int = int(52 * DECKS_COUNT * 0.33)
    MAX_PLAYERS: int = 7
    SEED: int = rand.SEED


@dataclass
class Table:
    deck: decks.Deck
    dealer: playable.Dealer
    players: list[playable.BlackJackPlayer]
    config: TableConfig = field(default_factory=TableConfig)
    games_count: int = 0


def is_game_ended(table: Table) -> bool:
    return table.dealer.hand.state in hand.State.end_states()


def is_game_started(table: Table) -> bool:
    if table.dealer.hand:
        return True
    return False


def bet_are_placed(table: Table) -> bool:
    return all([playable.get_current_hand(player).bet for player in table.players])


def get_current_moving_player(table: Table) -> playable.BlackJackPlayer | None:
    for player in table.players:
        if playable.get_current_hand(player) == hand.State.MOVING:
            return player
    return None


def add_player(table: Table, player: playable.BlackJackPlayer) -> playable.BlackJackPlayer:
    table.players.append(player)
    Events.run_event(Events.ON_PLAYER_JOINED, table, player)
    return player


def remove_player(table: Table, player: playable.BlackJackPlayer, kicked: bool) -> None:
    table.players.remove(player)
    if kicked:
        return Events.run_event(Events.ON_PLAYER_KICKED, table, player)
    Events.run_event(Events.ON_PLAYER_QUIT, table, player)


def reset_game(table: Table) -> None:
    playable.reset_hand(table.dealer)

    for player in table.players.copy():
        playable.reset_hands(player)
        if player.chips <= 0:
            remove_player(table, player, kicked=True)

    _update_deck(table)
    Events.run_event(Events.ON_GAME_RESET, table)


def _shuffle(table: Table) -> None:
    rand_state = table.config.RAND_STATE
    table.config.RAND_STATE = rand.shuffle(table.deck, rand_state)


def _update_deck(table: Table) -> None:
    if table.config.DECKS_COUNT == 1 or len(table.deck) < table.config.REMAINING_CARDS_FOR_SHUFFLING:
        table.deck.clear()
        decks.populate(table.deck, table.config.DECKS_COUNT)
        _shuffle(table)


def _start_new_game(table: Table) -> None:
    for player in table.players:
        decks.hand_out_last_cards(table.deck, playable.get_current_hand(player), 2)

    playable.get_current_hand(table.players[0]).state = hand.State.MOVING
    decks.hand_out_last_cards(table.deck, table.dealer.hand, 2)
    table.games_count += 1

    Events.run_event(Events.ON_GAME_STARTED, table)


def _process_move(table: Table, player: playable.BaseBlackJackPlayable, player_hand: hand.BlackJackHand) -> None:
    player_move: playable.Move = playable.make_move(player)

    if hand.is_busted(player_hand) or player_move == playable.Move.NONE:
        return

    if player_move == playable.Move.STAND:
        player_hand.state = hand.State.ENOUGH
    elif player_move == playable.Move.HIT:
        decks.hand_out_last_cards(table.deck, player_hand, count=1)
        player_hand.state = hand.State.ENOUGH if hand.is_busted(player_hand) else player_hand.state

    if table.dealer == player or not isinstance(player, playable.BlackJackPlayer):
        return

    match player_move:

        case playable.Move.DOUBLE:
            if not playable.can_double(player):
                raise exceptions.PlayerActionFailure(player.name, "double")

            decks.hand_out_last_cards(table.deck, player_hand, 1)

            player_hand.state = hand.State.ENOUGH
            playable.place_bet(player, player_hand.bet, player_hand)

        case playable.Move.SPLIT:
            if not playable.can_split(player, table.config.MAX_SPLITS):
                raise exceptions.PlayerActionFailure(player.name, "split")
            playable.split(player)

        case playable.Move.INSURANCE:
            if not playable.can_get_insurance(player, table.dealer):
                raise exceptions.PlayerActionFailure(player.name, "insurance")
            playable.apply_insurance(player)

        case playable.Move.EVEN_MONEY:
            if not playable.can_even_money(player, table.dealer):
                raise exceptions.PlayerActionFailure(player.name, "even money")
            player_hand.state = hand.State.EVEN_MONEY

    next_hand = playable.get_current_hand(player)
    if next_hand.state == hand.State.WAIT:
        next_hand.state = hand.State.MOVING


def __set_player_hand_game_result(table: Table, player_hand: hand.BlackJackHand) -> None:

    if player_hand.state == hand.State.EVEN_MONEY:
        return

    state = hand.State.LOSE
    dealer_hand = table.dealer.hand

    dealer_busted = hand.is_busted(dealer_hand)
    player_hand_busted = hand.is_busted(player_hand)

    dealer_score = hand.get_score(dealer_hand)
    player_hand_score = hand.get_score(player_hand)

    if dealer_busted and player_hand_busted and player_hand_score < dealer_score:
        state = hand.State.WIN
    elif dealer_busted and not player_hand_busted:
        state = hand.State.WIN
    elif not dealer_busted and not player_hand_busted:
        if player_hand_score > dealer_score:
            state = hand.State.WIN
        elif player_hand_score == dealer_score:
            state = hand.State.PUSH

    player_hand.state = state


def _set_end_results(table: Table) -> None:
    dealer_chips_before_end_game: int = table.dealer.chips
    for player in table.players:
        for player_hand in player.hands:

            reward: int = player_hand.bet
            __set_player_hand_game_result(table, player_hand)

            if player_hand.state == hand.State.WIN or player_hand.state == hand.State.EVEN_MONEY:
                if hand.get_score(player_hand) == 21 and not player_hand.state == hand.State.EVEN_MONEY:
                    reward += (player_hand.bet // 2)

                playable.give_chips(table.dealer, player, reward)

                player.chips += player_hand.bet
            elif player_hand.state == hand.State.PUSH:
                player.chips += player_hand.bet
            elif player_hand.state == hand.State.LOSE:
                table.dealer.chips += player_hand.bet

        if not player.insurance:
            continue

        insurance: int = player.insurance // 2
        if hand.get_score(table.dealer.hand) == 21:
            playable.give_chips(table.dealer, player, player.insurance - insurance)
            player.chips += insurance
        else:
            table.dealer.chips += insurance

    if dealer_chips_before_end_game < table.dealer.chips:
        table.dealer.hand.state = hand.State.WIN
    elif dealer_chips_before_end_game > table.dealer.chips:
        table.dealer.hand.state = hand.State.LOSE
    else:
        table.dealer.hand.state = hand.State.PUSH


def update(table: Table) -> None:

    if is_game_ended(table):
        raise exceptions.GameIsEnded

    if bet_are_placed(table) and not is_game_started(table):
        return _start_new_game(table)

    for idx, player in enumerate(table.players):
        player_hand = playable.get_current_hand(player)
        if player_hand.state != hand.State.MOVING:
            continue

        _process_move(table, player, player_hand)

        player_hand = playable.get_current_hand(player)

        if player_hand.state not in (hand.State.ENOUGH, hand.State.EVEN_MONEY):
            continue

        next_hand = table.players[idx+1].hands[0] if idx+1 < len(table.players) else table.dealer.hand
        next_hand.state = hand.State.MOVING

    if not table.dealer.hand.state != hand.State.MOVING:
        return

    _process_move(table, table.dealer, table.dealer.hand)

    if table.dealer.hand.state != hand.State.ENOUGH:
        return

    _set_end_results(table)
    Events.run_event(Events.ON_GAME_ENDED, table)
