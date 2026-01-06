from datetime import date, datetime, timedelta
import json
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from collections import defaultdict
import calendar
# event class stored in separate file for cleanliness
from Event import Event

# helper function for Ledger:
    # Take date and return the same day number of the following month
def add_one_month(d: datetime.date) -> datetime.date:
    year = d.year + (d.month // 12)
    month = d.month % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    # return datetime.date(year, month, day)
    # print(date(year, month, day))
    return date(year, month, day)


class Ledger:
    def __init__(self):
        # base events list:
        #   Will contain enough info to populate calendar. 
        #   This is nice to have so that we can reconstruct calendar with a different timeframe if needed.
        self.start_date = datetime.now().date()
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

    def populate_calendar(self, start_date, timeframe):
        # reset calendar each time this is called
        self.calendar = defaultdict(lambda: {'events': [], 'day_total': 0.0, 'balance': 0.0})
        for event in self.events:
            day = event.date
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
                    # print(day)
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
            print(day)
            balance += self.calendar[day]["day_total"]
            self.calendar[day]["balance"] = balance
            day += timedelta(days=1)
        pass

class GUI(tk.Tk):
    # self is the window - no need to pass root around
    def __init__(self):
        super().__init__()
        self.title("Ledger Application")
        # self.geometry("600x400")

        # -- Data Structures Initialization -- #

        self.ledger = Ledger()

        ########################
        # -- calendar frame -- #
        ########################
        cal_frame = ttk.Frame(self, padding=10)
        cal_frame.pack(fill="both", expand=True)
        
        # -- calendar widget -- #
        self.cal = Calendar(self,selectmode="day",year=datetime.now().year,month=datetime.now().month,day=datetime.now().day)
        self.cal.pack(padx=10,pady=10,fill="both",expand=True)

            # - bind date select - #
        def on_date_select(event):
            # selected_date = datetime.strptime(self.cal.get_date(), "%m/%d/%y").date()
            selected_date = self.cal.selection_get()
            sel_date_var.set(f"{selected_date}")
            day_info = self.ledger.calendar.get(selected_date)
            try:
                day_total_var.set(f"{day_info['day_total']:.2f}")
                day_balance_var.set(f"{day_info['balance']:.2f}")
            except:
                day_total_var.set("0.00")
                day_balance_var.set("0.00")
        
            update_day_events_list(selected_date)

        self.cal.bind("<<CalendarSelected>>", on_date_select)

        
        ####################
        # -- Grid frame -- # 
        ####################
        main_frame = ttk.Frame(self, padding=10)
        # what is fill ? 
        main_frame.pack(fill="both", expand=True)

        # -- row 0 -- #
            # - selected date - # 

                # save var to change on date select # 
        sel_date_var = tk.StringVar(value=f"{datetime.strptime(self.cal.get_date(), "%m/%d/%y").date()}")
        r0c0 = ttk.Entry(main_frame, textvariable=sel_date_var)
        r0c0.config(state="readonly")
        r0c0.grid(row=0, column=0, padx=5, pady=5)

            # - day total - #
        day_total_var = tk.StringVar(value="0.00")
        r0c1 = ttk.Entry(main_frame, textvariable=day_total_var)
        r0c1.config(state="readonly")
        r0c1.grid(row=0, column=1, padx=5, pady=5)
            # - day balance - #
        day_balance_var = tk.StringVar(value="0.00")
        r0c2 = ttk.Entry(main_frame, textvariable=day_balance_var)
        r0c2.config(state="readonly")
        r0c2.grid(row=0, column=2, padx=5, pady=5)

        # -- row 2 -- # 
            # - Add Event Button - #
        add_event_btn = ttk.Button(main_frame, text="Add Event", command=self.open_add_event_window)
        add_event_btn.grid(row=2, column=0, padx=3, pady=5)

            # - Save Events Button - #
        save_events_btn = ttk.Button(main_frame, text="Save Events", command=self.save_events)
        save_events_btn.grid(row=2, column=1, padx=3, pady=5)

            # -- Load Events Button -- #
        load_events_btn = ttk.Button(main_frame, text="Load Events", command=self.load_events)
        load_events_btn.grid(row=2, column=2, padx=3, pady=5)

        ####################
        # -- Data Frame -- #
        ####################
        data_frame = ttk.Frame(self, padding=10)
        data_frame.pack(fill="both", expand=True)

        def refresh_event_list():
            event_list.delete(0, tk.END)
            for event in self.ledger.events:
                event_list.insert(tk.END, f"{event.to_dict()}")
        refresh_btn = ttk.Button(data_frame, text="Refresh Event List", command=refresh_event_list)
        refresh_btn.pack(pady=5)

            # - Day Event List - #
        def update_day_events_list(selected_date):
            day_event_list.delete(0, tk.END)
            day_info = self.ledger.calendar.get(selected_date, {'events': []})
            for event in day_info['events']:
                day_event_list.insert(tk.END, f"{event.name} : {event.amount} : balance: {self.ledger.calendar[selected_date]['balance']:.2f}")

        day_event_list = tk.Listbox(data_frame)
        day_event_list.pack(fill="both", expand=True)
        update_day_events_list(datetime.strptime(self.cal.get_date(), "%m/%d/%y").date())


            # - Event List - #
        event_list = tk.Listbox(data_frame)
        event_list.pack(fill="both", expand=True)

            # - populate event list - #
        
        refresh_event_list()


            # - on event select - #
        def on_event_select(event):
            sel = event_list.curselection()
            if sel:
                index = sel[0]
                selected_event = self.ledger.events[index]
                print(f"Selected Event: {selected_event.name}, Date: {selected_event.date}, Amount: {selected_event.amount}")
        
        event_list.bind("<<ListboxSelect>>", on_event_select)


    def open_add_event_window(self):

        add_event_window = tk.Toplevel(self)
        
        add_event_window.title("Add Event")
        # add_event_window.geometry("300x200")
        
        # -- Event Name -- #
        ttk.Label(add_event_window, text="Event Name:").pack(pady=5)
        name_entry = ttk.Entry(add_event_window)
        name_entry.pack(pady=5)

        # -- Event Date -- #
        # taken from calendar widget in main window

        # -- Event Amount -- #
        ttk.Label(add_event_window, text="Event Amount:").pack(pady=5)
        amount_entry = ttk.Entry(add_event_window)
        amount_entry.pack(pady=5, padx=10)

        # -- Monthly Checkbox -- #
        def toggle_period_entry():
            if monthly_var.get():
                period_entry.config(state="disabled")
            else:
                period_entry.config(state="normal")

        monthly_var = tk.BooleanVar()
        monthly_check = ttk.Checkbutton(add_event_window, text="Monthly", variable=monthly_var, command=toggle_period_entry)
        monthly_check.pack(pady=5)

        # -- Period Entry -- #
        ttk.Label(add_event_window, text="Period (days):").pack(pady=5)
        period_entry = ttk.Entry(add_event_window)  
        period_entry.pack(pady=5)

        # -- Submit Button -- #
        def submit_event():

            e_flag = False

            # - name - #
            name = name_entry.get()
            if not name:
                name = "Unnamed Event"

            # - amount - #
            try:
                amount = float(amount_entry.get())
            except ValueError:
                e_flag = True
                amount = 0.0
            
            # - date - #
            date_selected = datetime.strptime(self.cal.get_date(), "%m/%d/%y").date()
            monthly = monthly_var.get()
            period = int(period_entry.get()) if not monthly and period_entry.get() else None

            self.ledger.add_event(name=name, date=date_selected, amount=amount, monthly=monthly, period=period)
            self.ledger.populate_calendar(self.ledger.start_date, datetime.now().date() + timedelta(days=1000))
            add_event_window.destroy()

        submit_btn = ttk.Button(add_event_window, text="Submit", command=submit_event)
        submit_btn.pack(pady=10)

    def save_events(self):
        with open("events.txt", "w") as f:
            json.dump(
                {
                    "start_date": self.ledger.start_date.isoformat(),                           # start date of ledger required to reconstruct calendar
                    "events": [event.to_dict() for event in self.ledger.events]
                },
                f # file object
                )

    def load_events(self):
        with open("events.txt", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.ledger.events = [Event.from_dict(item) for item in data.get("events")]
            self.ledger.start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date()
        self.ledger.populate_calendar(self.ledger.start_date, datetime.now().date() + timedelta(days=1000))

            


gui = GUI()
gui.mainloop()