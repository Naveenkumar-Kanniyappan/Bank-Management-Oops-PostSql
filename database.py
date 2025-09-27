import psycopg2
from psycopg2 import sql
import sys

class Database:
    def __init__(self, dbname, user, password, host="localhost", port=5432):
        try:
            self.conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            self.cur = self.conn.cursor()
            print("Database connection established successfully")
        except Exception as e:
            print("Database connection failed:", e)
            sys.exit(1)

    def create_tables(self):
        try:
            create_accounts = """
            CREATE TABLE IF NOT EXISTS accounts (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(200) NOT NULL,
                email VARCHAR(200) UNIQUE NOT NULL,
                balance NUMERIC(12,2) NOT NULL DEFAULT 0.00
            );
            """
            create_txns = """
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                description TEXT NOT NULL,
                timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW())
            );
            """
            self.cur.execute(create_accounts)
            self.cur.execute(create_txns)
            self.conn.commit()
            print("Tables created successfully")
        except Exception as e:
            print("Error creating tables:", e)
            self.conn.rollback()

    def add_account(self, username, password, email):
        try:
            self.cur.execute(
                "INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s) RETURNING id",
                (username, password, email)
            )
            new_id = self.cur.fetchone()[0]
            self.conn.commit()
            return new_id
        except psycopg2.errors.UniqueViolation:
            self.conn.rollback()
            return None
        except Exception as e:
            self.conn.rollback()
            print("Error adding account:", e)
            return None

    def get_account_by_username(self, username):
        try:
            self.cur.execute(
                "SELECT id, username, password, email, balance FROM accounts WHERE username = %s",
                (username,)
            )
            return self.cur.fetchone()
        except Exception as e:
            print("Error fetching account by username:", e)
            return None

    def get_account_by_email(self, email):
        try:
            self.cur.execute(
                "SELECT id, username, password, email, balance FROM accounts WHERE email = %s",
                (email,)
            )
            return self.cur.fetchone()
        except Exception as e:
            print("Error fetching account by email:", e)
            return None

    def get_account_by_credentials(self, username, password):
        try:
            self.cur.execute(
                "SELECT id, username, password, email, balance FROM accounts WHERE username = %s AND password = %s",
                (username, password)
            )
            return self.cur.fetchone()
        except Exception as e:
            print("Error verifying credentials:", e)
            return None

    def update_balance(self, account_id, new_balance):
        try:
            self.cur.execute(
                "UPDATE accounts SET balance = %s WHERE id = %s",
                (new_balance, account_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print("Error updating balance:", e)
            return False

    def add_transaction(self, account_id, description):
        try:
            self.cur.execute(
                "INSERT INTO transactions (account_id, description) VALUES (%s, %s)",
                (account_id, description)
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print("Error adding transaction:", e)
            return False

    def get_transactions(self, account_id):
        try:
            self.cur.execute(
                "SELECT description, timestamp FROM transactions WHERE account_id = %s ORDER BY timestamp DESC",
                (account_id,)
            )
            return self.cur.fetchall()
        except Exception as e:
            print("Error fetching transactions:", e)
            return []

    def close(self):
        try:
            self.cur.close()
            self.conn.close()
            print("Database connection closed")
        except Exception as e:
            print("Error closing database:", e)