from datetime import date, datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from collections import defaultdict

# lets have a dict of days containing events
calendar = {}



class Event:
    def __init__(self, name: str, date: datetime.date, amount: float, monthly: bool = False, period: int = None):
        self.name = name
        self.date = date
        self.amount = amount
        self.monthly = monthly
        self.period = period


    # the date format might not be correct here
    def to_dict(self):
        return {
            "name": self.name,
            # "date": self.date.isoformat(), "YYYY-MM-DD"
            "date": self.date.day(), #month(), #year()
            "amount": self.amount,
            "monthly": self.monthly,
            "period": self.period
        }

# helper function for Ledger:
    # Take date and return the same day number of the following month
# test this for correctness ...
def add_one_month(d: datetime.date) -> datetime.date:
    year = d.year + (d.month // 12)
    month = d.month % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


class Ledger:
    def __init__(self):
        # base events list:
        #   Will contain enough info to populate calendar. 
        #   This is nice to have so that we can reconstruct calendar with a different timeframe if needed.
        self.events = []
        self.calendar = defaultdict(lambda: {'events': [], 'day_total': 0.0, 'balance': 0.0})
        
    def add_event(self,
                  name: str, 
                  date: datetime.date,
                  amount: float,
                  monthly: bool = False,
                  period: int = None
                  ):
        event = Event(name=name, date=date, amount=amount, monthly=monthly, period=period)
        self.events.append(event)

    def populate_calendar(self, timeframe):
        # reset calendar each time this is called
        self.calendar = defaultdict(lambda: {'events': [], 'day_total': 0.0, 'balance': 0.0})
        for event in self.events:
            start_date = event.date
            day = start_date
            self.calendar[day]["day_total"] = 0.0  # ensure day is initialized
            if event.monthly:
                while day <= timeframe:
                    self.calendar[day]["events"].append(event)
                    self.calendar[day]["day_total"] += event.amount
                    # self.calendar[day]["balance"] += event.amount

                    # next occurance
                    day = add_one_month(day)
            elif event.period is not None:
                while day <= timeframe:
                    self.calendar[day]["events"].append(event)
                    self.calendar[day]["day_total"] += event.amount
                    # self.calendar[day]["balance"] += event.amount

                    # next occurance
                    day += timedelta(days = event.period)
            else:
                self.calendar[day]["events"].append(event)
                self.calendar[day]["day_total"] += event.amount
        balance = 0.0
        day = start_date
        # for day in sorted(self.calendar.keys()):
        while day <= timeframe:
            balance += self.calendar[day]["day_total"]
            self.calendar[day]["balance"] = balance
            day += timedelta(days=1)
        pass






if __name__ == "__main__":


    # 0) Env setup
    ledger = Ledger()

    # 1) Initialize root
    root = tk.Tk()
    root.geometry("420x360")

    # 2) Calendar widget
    cal = Calendar(
        root,
        selectmode="day",
        year=datetime.now().year,
        month=datetime.now().month,
        day=datetime.now().day,
    )
    cal.pack(
        padx=10,
        pady=10,
        fill="both",
        expand=True,
    )        
    tk.Label(root, text=f"Day Summary for {datetime.strptime(cal.get_date(), "%m/%d/%y").date()}").pack(anchor="e", padx=10, pady=(10,10))
    day_total_var = tk.StringVar(value=f"{ledger.calendar[datetime.strptime(cal.get_date(), "%m/%d/%y").date()]["day_total"]:.2f}")
    day_amt_view = tk.Entry(root, textvariable=day_total_var)
    day_amt_view.config(state="readonly")
    day_amt_view.pack(fill="x", padx=2, pady=(2,2))

    day_balance_var = tk.StringVar(value=f"{ledger.calendar[datetime.strptime(cal.get_date(), "%m/%d/%y").date()]["balance"]:.2f}")
    day_balance_view = tk.Entry(root, textvariable=day_balance_var)
    day_balance_view.config(state="readonly")
    day_balance_view.pack(fill="x", padx=2, pady=(4,4))
    # bind calendar to date selection event #
    def on_date_select(event):
        selected_date = datetime.strptime(cal.get_date(), "%m/%d/%y").date()
        # day_total_var.set(f"{ledger.calendar[selected_date]['day_total']:.2f}")
        # day_balance_var.set(f"{ledger.calendar[selected_date]['balance']:.2f}")
        
        # -- updating from a thread -- #
        root.after(0, lambda: day_total_var.set(f"{ledger.calendar[selected_date]['day_total']:.2f}"))
        root.after(0, lambda: day_balance_var.set(f"{ledger.calendar[selected_date]['balance']:.2f}"))
        
        print(f"{ledger.calendar[selected_date]['balance']:.2f}")

    cal.bind("<<CalendarSelected>>", on_date_select)

    def open_add_event_window():
        popup = tk.Toplevel(root)
        popup.geometry("320x320")
        popup.transient(root)   # keep it on top of the main window
        popup.grab_set()        # keep it in focus

        # ---- labels and entries ---- #
        tk.Label(popup, text="Event Name").pack(anchor="w", padx=10, pady=(10, 0)) # lookup how pack works + its args
        name_entry = tk.Entry(popup)
        name_entry.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(popup, text="Amount").pack(anchor="w", padx=10, pady=(10, 0))
        amount_entry = tk.Entry(popup)


        amount_entry.pack(fill="x", padx=10, pady=(0, 10))
        tk.Label(popup, text="Monthly").pack(anchor="w", padx=10, pady=(10, 0))
        
        def toggle_period_entry():
            if monthly_var.get():
                period_entry.config(state="disabled")
            else:
                period_entry.config(state="normal")

        monthly_var = tk.BooleanVar()
        monthly_check = tk.Checkbutton(popup, variable=monthly_var, command=toggle_period_entry)
        monthly_check.pack(anchor="w", padx=10, pady=(0, 10))

        tk.Label(popup, text="Period (days)").pack(anchor="w", padx=10, pady=(10, 0))
        period_entry = tk.Entry(popup)
        period_entry.pack(fill="x", padx=10, pady=(0, 10))

        def submit_event():
            ## error flag to stop submission on error ##
            e_flag = False


            # -- get name -- #
            name = name_entry.get()
            if not name:
                name = "Unnamed Event"
            # -- get amount -- #
            try:
                amount = float(amount_entry.get())
            except ValueError:
                tk.Label(popup, text="Invalid amount. Please enter a number.", fg="red").pack()
                e_flag = True

            # -- get monthly checkbox val -- #
            monthly = monthly_var.get()
            
            # -- get period -- #
            if not monthly:
                period = period_entry.get()
                try:
                    period = int(period)
                except ValueError:
                    period = None

            selected_date = cal.get_date()
            
            date_obj = datetime.strptime(selected_date, "%m/%d/%y").date()



            # if error flag is raised, return from submit event without adding event # 
            if e_flag:
                return
            

            ledger.add_event(name, date_obj, amount, monthly, period)
            ledger.populate_calendar(date(2026, 5, 1))  # Example timeframe

            popup.destroy()

        submit_btn = tk.Button(
            popup,
            text="Submit",
            command=submit_event
        ).pack(pady=10)

    add_event_btn = tk.Button(
        root,
        text="Add Event",
        command=open_add_event_window
    ).pack(pady=10)

    


    root.mainloop()