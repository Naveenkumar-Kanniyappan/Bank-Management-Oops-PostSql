from database import Database
from bank_system_db import BankSystem

def get_numeric_input(prompt, min_value=None, max_value=None):
    while True:
        try:
            value = int(input(prompt))
            if min_value is not None and value < min_value:
                print(f"Value must be at least {min_value}")
                continue
            if max_value is not None and value > max_value:
                print(f"Value must be at most {max_value}")
                continue
            return value
        except ValueError:
            print("Please enter a valid number")

def get_float_input(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid amount")

def user_menu(bank_system, user):
    while True:
        print("\n" + "="*80)
        print(f"\nWelcome, {user.username}")
        print("\n" + "="*80)

        print("1. Check Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Transfer Money")
        print("5. View Transactions")
        print("6. Logout\n")
        
        choice = get_numeric_input("Select option: ", 1, 6)
        
        if choice == 1:
            balance = user.get_balance()
            print(f"Current Balance: ${balance:.2f}")
            
        elif choice == 2:
            amount = get_float_input("Enter deposit amount: ")
            user.deposit(amount)
            
        elif choice == 3:
            amount = get_float_input("Enter withdrawal amount: ")
            user.withdraw(amount)
            
        elif choice == 4:
            receiver_email = input("Enter receiver email address: ")
            amount = get_float_input("Enter transfer amount: ")
            user.transfer(receiver_email, amount)
            
        elif choice == 5:
            user.view_transactions()
            
        elif choice == 6:
            print("Logged out successfully")
            break

def main():
    try:
        db = Database(dbname="Bank-Management-Api", user="dckap", password="welcome", host="localhost", port=5432)
        db.create_tables()
        bank_system = BankSystem(db)
        
        while True:
            print("\n" + "="*80)
            print("\nBanking System")
            print("\n" + "="*80)
            
            print("1. Login")
            print("2. Create Account")
            print("3. Exit\n")

            
            choice = get_numeric_input("Select option: ", 1, 3)
            
            if choice == 1:
                username = input("Username: ")
                password = input("Password: ")
                user = bank_system.login(username, password)
                if user:
                    user_menu(bank_system, user)
                    
            elif choice == 2:
                username = input("Choose username: ")
                email = input("Email address: ")
                password = input("Choose password: ")
                bank_system.signup(username, password, email)
                
            elif choice == 3:
                print("Thank you for using our banking system")
                break
                
    except Exception as e:
        print("System error:", e)
        
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    main()