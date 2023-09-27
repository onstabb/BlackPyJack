

class BlackJackException(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args)


class PlayerActionFailure(BlackJackException):

    def __init__(self, name: str, action: str):
        super().__init__(f"{name} cannot perform `{action}`")


class GameIsEnded(BlackJackException):
    pass
