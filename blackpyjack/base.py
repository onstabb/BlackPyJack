from typing import Any


class BaseBlackJackEntity:

    def to_dict(self) -> dict[str, Any]:
        ...

