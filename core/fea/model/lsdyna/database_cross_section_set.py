from dataclasses import dataclass


@dataclass
class DatabaseCrossSectionSet:
    uid: int
    name: str
    node_ids: tuple
    element_ids: tuple
