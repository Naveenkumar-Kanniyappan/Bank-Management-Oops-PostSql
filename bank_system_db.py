from database import Database

class Account:
    def __init__(self, db, account_id, username, password, email, balance):
        self.db = db
        self.id = account_id
        self.username = username
        self.password = password
        self.email = email
        self.balance = float(balance)

    def refresh_balance(self):
        try:
            row = self.db.get_account_by_username(self.username)
            if row:
                self.balance = float(row[4])
            return True
        except Exception as e:
            print("Error refreshing balance:", e)
            return False

    def deposit(self, amount):
        if not self._validate_amount(amount, "deposit"):
            return False
        
        try:
            self.balance += amount
            if self.db.update_balance(self.id, self.balance):
                description = f"Deposit: ${amount:.2f}"
                self.db.add_transaction(self.id, description)
                print(f"Deposit successful. New balance: ${self.balance:.2f}")
                return True
            return False
        except Exception as e:
            print("Deposit failed:", e)
            return False

    def withdraw(self, amount):
        if not self._validate_amount(amount, "withdrawal"):
            return False
        
        if amount > self.balance:
            print("Insufficient funds")
            return False
        
        try:
            self.balance -= amount
            if self.db.update_balance(self.id, self.balance):
                description = f"Withdrawal: ${amount:.2f}"
                self.db.add_transaction(self.id, description)
                print(f"Withdrawal successful. New balance: ${self.balance:.2f}")
                return True
            return False
        except Exception as e:
            print("Withdrawal failed:", e)
            return False

    def transfer(self, receiver_email, amount):
        if not self._validate_amount(amount, "transfer"):
            return False
        
        if amount > self.balance:
            print("Insufficient funds for transfer")
            return False

        if receiver_email.lower() == self.email.lower():
            print("Cannot transfer money to yourself")
            return False

        try:
            receiver_data = self.db.get_account_by_email(receiver_email)
            if not receiver_data:
                print("Receiver account not found with this email address")
                return False

            receiver_id, rec_username, rec_pwd, rec_email, rec_balance = receiver_data
            receiver_balance = float(rec_balance)

            print(f"\nTransfer Details:")
            print(f"From: {self.username} ({self.email})")
            print(f"To: {rec_username} ({rec_email})")
            print(f"Amount: ${amount:.2f}")
            
            confirm = input("Confirm transfer? (yes/no): ").lower()
            if confirm not in ['yes', 'y']:
                print("Transfer cancelled")
                return False

            self.balance -= amount
            if not self.db.update_balance(self.id, self.balance):
                return False

            new_receiver_balance = receiver_balance + amount
            if not self.db.update_balance(receiver_id, new_receiver_balance):
 
                self.balance += amount
                self.db.update_balance(self.id, self.balance)
                print("Transfer failed due to system error")
                return False

            self.db.add_transaction(self.id, f"Transfer to {rec_username} ({rec_email}): ${amount:.2f}")
            self.db.add_transaction(receiver_id, f"Transfer from {self.username} ({self.email}): ${amount:.2f}")

            print(f"Transfer completed successfully!")
            print(f"New balance: ${self.balance:.2f}")
            return True
            
        except Exception as e:
            print("Transfer failed:", e)
            return False

    def view_transactions(self):
        try:
            self.refresh_balance()
            
            transactions = self.db.get_transactions(self.id)
            
            print("\n" + "="*80)
            print("TRANSACTION HISTORY")
            print("="*80)
            
            if not transactions:
                print("No transactions found")
            else:
                for description, timestamp in transactions:
                    print(f"{timestamp} - {description}")
            
            print("-"*50)
            print(f"CURRENT BALANCE: ${self.balance:.2f}")
            print("="*50)
            
        except Exception as e:
            print("Error viewing transactions:", e)

    def get_balance(self):
        if self.refresh_balance():
            return self.balance
        return 0.0

    def _validate_amount(self, amount, operation):
        try:
            amount = float(amount)
            if amount <= 0:
                print(f"Amount must be positive for {operation}")
                return False
            return True
        except ValueError:
            print("Invalid amount format")
            return False


class BankSystem:
    def __init__(self, db):
        self.db = db

    def signup(self, username, password, email):
        if not self._validate_input(username, email, password):
            return None

        try:
            if self.db.get_account_by_username(username):
                print("Username already exists")
                return None

            if self.db.get_account_by_email(email):
                print("Email address already registered")
                return None

            new_account_id = self.db.add_account(username, password, email)
            if new_account_id:
                print("Account created successfully")
                account_data = self.db.get_account_by_username(username)
                return Account(self.db, *account_data)
            return None
            
        except Exception as e:
            print("Signup failed:", e)
            return None

    def login(self, username, password):
        if not username or not password:
            print("Username and password are required")
            return None

        try:
            account_data = self.db.get_account_by_credentials(username, password)
            if account_data:
                print("Login successful")
                return Account(self.db, *account_data)
            else:
                print("Invalid username or password")
                return None
        except Exception as e:
            print("Login failed:", e)
            return None

    def _validate_input(self, username, email, password):
        if not username or len(username) < 3:
            print("Username must be at least 3 characters long")
            return False

        if not email or '@' not in email:
            print("Valid email address is required")
            return False
        

        if not password or len(password) < 4:
            print("Password must be at least 4 characters long")
            return False
        
        return True