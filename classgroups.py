"""Scrutini Class Groupings.

Representing intermediary classes that allow for a better understanding of
the data.
"""
import classes as sc


class SCEvent:
    def __init__(self, id, db):
        self.db = db
        self.event = self.db.tables.event.get(id)
        self.scores = self.db.tables.scores.get_by_event(id)
