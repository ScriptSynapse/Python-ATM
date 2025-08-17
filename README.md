# 🏦 Python ATM System (GUI)

A simple **ATM Simulation** built with **Python (Tkinter)** that allows users to login, deposit, withdraw, transfer funds, view mini-statements, and change their PIN. The system uses a **JSON file (`accounts.json`)** as a lightweight database to store account details and transactions.


## ✨ Features

* 🔐 **Secure Login** with Account Number & PIN
* 💰 **Deposit & Withdraw** (with per-transaction & daily limits)
* 🔄 **Fund Transfer** between accounts
* 📜 **Mini Statement** (last 10 transactions)
* 🔑 **Change PIN** (with validation)
* 📂 **Persistent Storage** using `accounts.json`
* 🖥️ **User-Friendly GUI** with Tkinter


## 📂 Project Structure

```
├── ATM.py          # Main program (GUI + logic)
├── accounts.json   # Account data storage
```

* **ATM.py** → Handles GUI, login, deposits, withdrawals, transfers, PIN changes, and transaction records.
* **accounts.json** → Stores user account details including balances, PINs, and transaction history.


## ⚙️ Installation & Usage

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/atm-system.git
cd atm-system
```

### 2. Run the ATM

```bash
python ATM.py
```


## 👤 Default Demo Accounts

The system comes with **preloaded demo accounts**:

| Account No | Name  | PIN  | Balance  |
| ---------- | ----- | ---- | -------- |
| `1001`     | Alice | 1234 | ₹100,000 |
| `1002`     | Bob   | 4321 | ₹50,000  |

You can also create or modify accounts directly in **`accounts.json`**.

## 💳 Transaction Rules

* **Daily Withdrawal Limit:** ₹20,000
* **Per Transaction Withdrawal Limit:** ₹10,000
* Transactions are stored (up to last 50 per account).


## 🚀 Future Enhancements

* 🔔 Email/SMS Alerts for transactions
* 🏦 Admin dashboard for account management
* 📊 Export statements as CSV/PDF
* 🌐 Move from JSON to a real database (SQLite/MySQL)


## 📝 License

This project is licensed under the **MIT License**.
Feel free to use and improve it!
