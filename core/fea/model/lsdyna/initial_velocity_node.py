from dataclasses import dataclass


@dataclass
class InitialVelocityNode:
    uid: int
    components: tuple
    cid: int = 0
