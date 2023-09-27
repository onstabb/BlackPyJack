import enum


class Events(enum.Enum):

    ON_PLAYER_KICKED = set()
    ON_PLAYER_JOINED = set()
    ON_PLAYER_QUIT = set()

    ON_GAME_RESET = set()
    ON_GAME_STARTED = set()
    ON_GAME_ENDED = set()

    @classmethod
    def run_event(cls, event: 'Events', *args, **kwargs):

        for callback in event.value:
            callback(*args, **kwargs)
