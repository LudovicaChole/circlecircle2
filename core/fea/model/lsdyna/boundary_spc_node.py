from dataclasses import dataclass


@dataclass
class BoundarySpcNode:
    uid: int
    dofs: tuple
    cid: int = 0
