import datetime

class Birthday:
    def __init__(self, name: str, date: datetime.date):
        self.name = name
        self.date = date

    def __str__(self):
        return f"name: {self.name}, day: {self.date.day}, month: {self.date.month}, year: {self.date.year}"