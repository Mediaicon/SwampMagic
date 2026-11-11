from dataclasses import dataclass


@dataclass(frozen=True)
class Topic:
    id: str
    name: str
    blurb: str        # what the journal says about it
