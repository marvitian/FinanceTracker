import datetime

class Event:
    def __init__(self, name: str, date: datetime.date, amount: float, monthly: bool = False, period: int = None):
        self.name = name
        self.date = date
        self.amount = amount
        self.monthly = monthly
        self.period = period



    

    def to_dict(self):
        return {
            "name": self.name,
            "date": self.date.isoformat(),  # "YYYY-MM-DD"
            "amount": self.amount,
            "monthly": self.monthly,
            "period": self.period
        }


    def from_dict(data):
        return Event(
            name=data["name"],
            date=datetime.date.fromisoformat(data["date"]),
            amount=data["amount"],
            monthly=data["monthly"],
            period=data["period"]
        )