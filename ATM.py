import json
import os
from datetime import datetime, date
from typing import Dict, Any, Optional

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

DATA_FILE = os.path.join(os.path.dirname(__file__), "accounts.json")

DAILY_WITHDRAW_LIMIT = 20000.00
PER_TX_WITHDRAW_LIMIT = 10000.00

# -----------------------------
# Data helpers
# -----------------------------
def load_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        demo = {
            "1001": {
                "name": "Alice",
                "pin": "1234",
                "balance": 100000.00,
                "daily_withdrawn": 0.0,
                "withdraw_date": str(date.today()),
                "transactions": []
            },
            "1002": {
                "name": "Bob",
                "pin": "4321",
                "balance": 50000.00,
                "daily_withdrawn": 0.0,
                "withdraw_date": str(date.today()),
                "transactions": []
            }
        }
        save_data(demo)
        return demo
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data: Dict[str, Any]) -> None:
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, DATA_FILE)

def ensure_withdraw_counters(acct: Dict[str, Any]):
    today = str(date.today())
    if acct.get("withdraw_date") != today:
        acct["withdraw_date"] = today
        acct["daily_withdrawn"] = 0.0

def add_tx(acct: Dict[str, Any], kind: str, amount: float, meta: str = ""):
    acct.setdefault("transactions", [])
    acct["transactions"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": kind,
        "amount": round(amount, 2),
        "balance": round(acct["balance"], 2),
        "meta": meta
    })
    acct["transactions"] = acct["transactions"][-50:]

# -----------------------------
# GUI
# -----------------------------
class ATMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python ATM")
        self.geometry("720x520")
        self.resizable(False, False)
        self.style = ttk.Style(self)
        if "vista" in self.style.theme_names():
            self.style.theme_use("vista")
        self.db: Dict[str, Any] = load_data()
        self.current_acct_id: Optional[str] = None

        self.container = ttk.Frame(self, padding=16)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (LoginPage, DashboardPage, StatementPage, TransferPage, PinPage):
            page = F(self.container, self)
            self.frames[F.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, name: str):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    # Helpers bound to actions
    def get_acct(self) -> Dict[str, Any]:
        return self.db[self.current_acct_id]

    def login(self, acct_id: str, pin: str) -> bool:
        if acct_id in self.db and self.db[acct_id].get("pin") == pin:
            self.current_acct_id = acct_id
            return True
        return False

    def logout(self):
        save_data(self.db)
        self.current_acct_id = None
        self.show_frame("LoginPage")

    def deposit(self, amount: float):
        acct = self.get_acct()
        acct["balance"] += amount
        add_tx(acct, "deposit", amount)
        save_data(self.db)

    def withdraw(self, amount: float) -> str:
        acct = self.get_acct()
        ensure_withdraw_counters(acct)
        if amount > PER_TX_WITHDRAW_LIMIT:
            return f"Per-transaction limit is ₹{PER_TX_WITHDRAW_LIMIT:,.2f}."
        if acct["balance"] < amount:
            return "Insufficient funds."
        if acct["daily_withdrawn"] + amount > DAILY_WITHDRAW_LIMIT:
            remaining = DAILY_WITHDRAW_LIMIT - acct["daily_withdrawn"]
            return f"Daily limit exceeded. You can still withdraw up to ₹{remaining:,.2f} today."
        acct["balance"] -= amount
        acct["daily_withdrawn"] += amount
        add_tx(acct, "withdrawal", amount)
        save_data(self.db)
        return ""

    def transfer(self, dest_id: str, amount: float) -> str:
        if dest_id not in self.db:
            return "Destination account not found."
        if dest_id == self.current_acct_id:
            return "Cannot transfer to the same account."
        src = self.get_acct()
        dest = self.db[dest_id]
        if src["balance"] < amount:
            return "Insufficient funds."
        src["balance"] -= amount
        dest["balance"] += amount
        add_tx(src, "transfer_out", amount, meta=f"to {dest_id}")
        add_tx(dest, "transfer_in", amount, meta=f"from {self.current_acct_id}")
        save_data(self.db)
        return ""

class LoginPage(ttk.Frame):
    def __init__(self, parent, app: ATMApp):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Welcome to Python ATM", font=("Segoe UI", 20, "bold")).pack(pady=20)

        form = ttk.Frame(self)
        form.pack(pady=10)

        ttk.Label(form, text="Account Number").grid(row=0, column=0, sticky="e", padx=8, pady=6)
        self.ent_acct = ttk.Entry(form, width=30)
        self.ent_acct.grid(row=0, column=1, pady=6)

        ttk.Label(form, text="PIN").grid(row=1, column=0, sticky="e", padx=8, pady=6)
        self.ent_pin = ttk.Entry(form, width=30, show="•")
        self.ent_pin.grid(row=1, column=1, pady=6)

        btn = ttk.Button(self, text="Login", command=self.do_login)
        btn.pack(pady=16)

        self.status = ttk.Label(self, text="", foreground="red")
        self.status.pack()

    def do_login(self):
        acct_id = self.ent_acct.get().strip()
        pin = self.ent_pin.get().strip()
        if self.app.login(acct_id, pin):
            self.ent_pin.delete(0, tk.END)
            self.status.config(text="")
            self.app.show_frame("DashboardPage")
        else:
            self.status.config(text="Invalid account or PIN.")

    def on_show(self):
        self.ent_acct.delete(0, tk.END)
        self.ent_pin.delete(0, tk.END)
        self.status.config(text="")

class DashboardPage(ttk.Frame):
    def __init__(self, parent, app: ATMApp):
        super().__init__(parent)
        self.app = app

        self.header = ttk.Label(self, text="", font=("Segoe UI", 16, "bold"))
        self.header.pack(anchor="w")

        bal_frame = ttk.Frame(self)
        bal_frame.pack(fill="x", pady=10)
        ttk.Label(bal_frame, text="Current Balance:", font=("Segoe UI", 12)).pack(side="left")
        self.lbl_balance = ttk.Label(bal_frame, text="₹0.00", font=("Segoe UI", 12, "bold"))
        self.lbl_balance.pack(side="left", padx=8)

        # Actions
        actions = ttk.Frame(self)
        actions.pack(pady=12)

        ttk.Button(actions, text="Deposit", width=18, command=self.do_deposit).grid(row=0, column=0, padx=8, pady=6)
        ttk.Button(actions, text="Withdraw", width=18, command=self.do_withdraw).grid(row=0, column=1, padx=8, pady=6)
        ttk.Button(actions, text="Transfer", width=18, command=lambda: self.app.show_frame("TransferPage")).grid(row=0, column=2, padx=8, pady=6)
        ttk.Button(actions, text="Mini Statement", width=18, command=lambda: self.app.show_frame("StatementPage")).grid(row=1, column=0, padx=8, pady=6)
        ttk.Button(actions, text="Change PIN", width=18, command=lambda: self.app.show_frame("PinPage")).grid(row=1, column=1, padx=8, pady=6)
        ttk.Button(actions, text="Logout", width=18, command=self.app.logout).grid(row=1, column=2, padx=8, pady=6)

    def on_show(self):
        acct = self.app.get_acct()
        self.header.config(text=f"Hello, {acct['name']} (Acc ****{str(self.app.current_acct_id)[-2:]})")
        self.lbl_balance.config(text=f"₹{acct['balance']:,.2f}")

    def prompt_amount(self, title: str) -> Optional[float]:
        amt_str = simpledialog.askstring("Amount", f"{title} amount (e.g., 500 or 500.00):", parent=self)
        if amt_str is None:
            return None
        try:
            amt = float(amt_str.replace(",", "").strip())
            if amt <= 0:
                raise ValueError
            return round(amt, 2)
        except Exception:
            messagebox.showerror("Invalid", "Please enter a positive number.")
            return None

    def do_deposit(self):
        amt = self.prompt_amount("Deposit")
        if amt is None: return
        self.app.deposit(amt)
        self.on_show()
        messagebox.showinfo("Success", f"Deposited ₹{amt:,.2f}.")

    def do_withdraw(self):
        amt = self.prompt_amount("Withdraw")
        if amt is None: return
        err = self.app.withdraw(amt)
        if err:
            messagebox.showwarning("Cannot withdraw", err)
        else:
            self.on_show()
            messagebox.showinfo("Success", f"Dispensed ₹{amt:,.2f}.")

class TransferPage(ttk.Frame):
    def __init__(self, parent, app: ATMApp):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Transfer Funds", font=("Segoe UI", 16, "bold")).pack(anchor="w")

        form = ttk.Frame(self)
        form.pack(pady=16)
        ttk.Label(form, text="Destination Account").grid(row=0, column=0, sticky="e", padx=8, pady=6)
        self.ent_dest = ttk.Entry(form, width=30)
        self.ent_dest.grid(row=0, column=1, pady=6)

        ttk.Label(form, text="Amount (₹)").grid(row=1, column=0, sticky="e", padx=8, pady=6)
        self.ent_amount = ttk.Entry(form, width=30)
        self.ent_amount.grid(row=1, column=1, pady=6)

        btns = ttk.Frame(self); btns.pack(pady=8)
        ttk.Button(btns, text="Send", command=self.do_transfer).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="Back", command=lambda: self.app.show_frame("DashboardPage")).grid(row=0, column=1, padx=6)

    def on_show(self):
        self.ent_dest.delete(0, tk.END)
        self.ent_amount.delete(0, tk.END)

    def do_transfer(self):
        dest = self.ent_dest.get().strip()
        try:
            amt = float(self.ent_amount.get().replace(",", "").strip())
            if amt <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Invalid", "Enter a positive amount.")
            return
        err = self.app.transfer(dest, round(amt, 2))
        if err:
            messagebox.showwarning("Transfer failed", err)
        else:
            messagebox.showinfo("Success", f"Transferred ₹{amt:,.2f} to {dest}.")
            self.app.show_frame("DashboardPage")

class StatementPage(ttk.Frame):
    def __init__(self, parent, app: ATMApp):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Mini Statement (last 10)", font=("Segoe UI", 16, "bold")).pack(anchor="w")

        self.tree = ttk.Treeview(self, columns=("time", "type", "amount", "balance", "meta"), show="headings", height=12)
        self.tree.pack(fill="both", expand=True, pady=8)
        for col, w in (("time", 150), ("type", 120), ("amount", 120), ("balance", 120), ("meta", 160)):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=w, anchor="center")

        ttk.Button(self, text="Back", command=lambda: self.app.show_frame("DashboardPage")).pack(pady=8)

    def on_show(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        txs = self.app.get_acct().get("transactions", [])[-10:]
        for t in txs:
            self.tree.insert("", "end", values=(t["time"], t["type"], f"₹{t['amount']:,.2f}", f"₹{t['balance']:,.2f}", t.get("meta","")))

class PinPage(ttk.Frame):
    def __init__(self, parent, app: ATMApp):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Change PIN", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        form = ttk.Frame(self); form.pack(pady=12)

        ttk.Label(form, text="Current PIN").grid(row=0, column=0, sticky="e", padx=8, pady=6)
        self.cur = ttk.Entry(form, show="•", width=30); self.cur.grid(row=0, column=1, pady=6)

        ttk.Label(form, text="New PIN (4-6 digits)").grid(row=1, column=0, sticky="e", padx=8, pady=6)
        self.n1 = ttk.Entry(form, show="•", width=30); self.n1.grid(row=1, column=1, pady=6)

        ttk.Label(form, text="Re-enter New PIN").grid(row=2, column=0, sticky="e", padx=8, pady=6)
        self.n2 = ttk.Entry(form, show="•", width=30); self.n2.grid(row=2, column=1, pady=6)

        btns = ttk.Frame(self); btns.pack(pady=8)
        ttk.Button(btns, text="Update", command=self.update_pin).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="Back", command=lambda: self.app.show_frame("DashboardPage")).grid(row=0, column=1, padx=6)

    def on_show(self):
        self.cur.delete(0, tk.END); self.n1.delete(0, tk.END); self.n2.delete(0, tk.END)

    def update_pin(self):
        acct = self.app.get_acct()
        if self.cur.get().strip() != acct.get("pin"):
            messagebox.showerror("Error", "Incorrect current PIN.")
            return
        new1 = self.n1.get().strip()
        new2 = self.n2.get().strip()
        if new1 != new2:
            messagebox.showerror("Error", "PINs do not match.")
            return
        if not new1.isdigit() or not (4 <= len(new1) <= 6):
            messagebox.showerror("Error", "PIN must be 4 to 6 digits.")
            return
        acct["pin"] = new1
        save_data(self.app.db)
        messagebox.showinfo("Success", "PIN updated successfully.")
        self.app.show_frame("DashboardPage")

if __name__ == "__main__":
    app = ATMApp()
    app.mainloop()
