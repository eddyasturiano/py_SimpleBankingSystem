import sqlite3
from random import randint


conn = sqlite3.connect("card.s3db")
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS card
               (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)""")
conn.commit()


def generate_checksum(number_str):
    subtotal = 0
    checksum = None
    digits_list_1 = [int(digit) for digit in number_str]
    digits_list_2 = [digits_list_1[i] * 2 if i % 2 == 0 else digits_list_1[i] for i in range(15)]
    digits_list_3 = [digit - 9 if digit > 9 else digit for digit in digits_list_2]
    for num in digits_list_3:
        subtotal += num
    for x in range(10):
        if (subtotal + x) % 10 == 0:
            checksum = x
            break
    return str(checksum)


def check_luhn_algo(number_str):
    digits_sum = int(number_str[-1])
    drop_last_digit = number_str[:len(number_str) - 1]
    step_1 = [int(digit) for digit in drop_last_digit]
    step_2 = [step_1[i] * 2 if i % 2 == 0 else step_1[i] for i in range(15)]
    step_3 = [digit - 9 if digit > 9 else digit for digit in step_2]
    for num in step_3:
        digits_sum += num
    if digits_sum % 10 == 0:
        return True
    else:
        return False


class Account:
    BIN = "400000"

    def __init__(self):
        self.acc_identifier = "".join(str(randint(0, 9)) for _ in range(9))
        self.generated_number = Account.BIN + self.acc_identifier
        self.card_number = self.generated_number + generate_checksum(self.generated_number)
        self.pin = "".join(str(randint(0, 9)) for _ in range(4))
        self.account_info = [self.card_number, self.pin]
        cur.execute("INSERT INTO card (number, pin) VALUES (?, ?)", self.account_info)
        conn.commit()


using_banking_sys = True
while using_banking_sys:
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")
    customer_action = input()

    if customer_action == "1":
        new_acc = Account()
        print("\nYour card has been created")
        print("Your card number:\n{}".format(new_acc.card_number))
        print("Your card PIN:\n{}\n".format(new_acc.pin))
    elif customer_action == "2":
        print("\nEnter your card number:")
        card_number = input()
        print("Enter your PIN:")
        pin = input()
        cur.execute("SELECT pin FROM card WHERE number=?", (card_number,))
        if cur.fetchone() == (pin,):
            print("\nYou have successfully logged in!\n")
            while True:
                print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")
                cur.execute("SELECT balance FROM card WHERE number=?", (card_number,))
                customer_balance = cur.fetchone()[0]
                logged_in_action = input()
                if logged_in_action == "1":
                    print("\nBalance: " + str(customer_balance) + "\n")
                elif logged_in_action == "2":
                    print("\nEnter income:")
                    income = int(input())
                    add_income_lst = [income, card_number]
                    cur.execute("UPDATE card SET balance=balance+? WHERE number=?", add_income_lst)
                    conn.commit()
                    print("Income was added!\n")
                elif logged_in_action == "3":
                    print("\nTransfer\nEnter card number:")
                    transfer_card_num = input()
                    cur.execute("SELECT id FROM card WHERE number=?", (transfer_card_num,))
                    transfer_card_id = cur.fetchone()
                    if card_number == transfer_card_num:
                        print("You can't transfer money to the same account!\n")
                    elif not check_luhn_algo(transfer_card_num):
                        print("Probably you made mistake in the card number. Please try again!\n")
                    elif transfer_card_id is None:
                        print("Such a card does not exist.\n")
                    else:
                        print("Enter how much money you want to transfer:")
                        transfer_amount = int(input())
                        if transfer_amount > customer_balance:
                            print("Not enough money!\n")
                        else:
                            customer_transfer_info = [transfer_amount, card_number]
                            transfer_info = [transfer_amount, transfer_card_num]
                            cur.execute("UPDATE card SET balance=balance-? WHERE number=?", customer_transfer_info)
                            cur.execute("UPDATE card SET balance=balance+? WHERE number=?", transfer_info)
                            conn.commit()
                            print("Success!\n")
                elif logged_in_action == "4":
                    cur.execute("DELETE FROM card WHERE number=?", (card_number,))
                    conn.commit()
                    print("\nThe account has been closed!\n")
                    break
                elif logged_in_action == "5":
                    print("\nYou have successfully logged out!\n")
                    break
                elif logged_in_action == "0":
                    using_banking_sys = False
                    break
        else:
            print("\nWrong card number or PIN!\n")
    elif customer_action == "0":
        using_banking_sys = False

conn.close()
print("\nBye!")
