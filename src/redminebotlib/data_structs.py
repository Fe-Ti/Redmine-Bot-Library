# Copyright 2023 Fe-Ti aka T.Kravchenko
from dataclasses import dataclass

@dataclass
class User:
    uid : str = None
    is_busy : bool = False # some sort of a lock

    state = None # A reference to actual state
    variables : dict() = None

@dataclass
class Message:
    user_id : str
    content : str
