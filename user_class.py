
from aiogram.dispatcher.filters.state import State, StatesGroup


class Pig:
    def __init__(self, name, weight, last_updated=None, chat_id=None):
        self.name = name
        self.weight = weight
        self.last_updated = last_updated

    def to_dict(self):
        return {
            "name": self.name,
            "weight": self.weight,
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name"),
            weight=data.get("weight"),
            last_updated=data.get("last_updated"),
        )

class PigRenameStates(StatesGroup):
    enter_new_name = State()