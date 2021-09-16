import json
import os
from datetime import datetime
import random
import string


def card_expiry_calculator():
    today = datetime.now()
    today_year = today.year
    today_month = today.month
    year = today_year+4
    month = today_month
    expiry_date = str(month) +"/"+ str(year)
    return expiry_date



def cvv_creation(length):
    digits = string.digits
    result_str = ''.join((random.choice(digits) for i in range(length)))
    return result_str



def debitcard_number_creation():

    if "data" not in os.listdir():
        os.mkdir("data")
    if "debitcard_no.json" not in os.listdir("data"):
        debitcard_no = 6080320011724000
        with open("data/debitcard_no.json", "w+") as f:
            json.dump(debitcard_no, f)
        return debitcard_no

    else:
        with open("data/debitcard_no.json", "r") as f:
            debitcard_no = json.load(f)
            debitcard_no += 1
        with open("data/debitcard_no.json", "w+") as f:
            json.dump(debitcard_no, f)
        return debitcard_no

def creditcard_number_creation():

    if "data" not in os.listdir():
        os.mkdir("data")
    if "credit_no.json" not in os.listdir("data"):
        credit_no = 4300424311001000
        with open("data/credit_no.json", "w+") as f:
            json.dump(credit_no, f)
        return credit_no

    else:
        with open("data/credit_no.json", "r") as f:
            credit_no = json.load(f)
            credit_no += 1
        with open("data/credit_no.json", "w+") as f:
            json.dump(credit_no, f)
        return credit_no






def dob_converter(dob):
    str1 = dob.split("/")
    formated_date = '-'.join(reversed(str1))
    return formated_date


def age_calculator(dob):
    today = datetime.now()
    today_year = today.year
    words = dob.split("-")
    year = int(words[0])
    age = str(today_year - year)
    return age




def account_number_creation():

    if "data" not in os.listdir():
        os.mkdir("data")
    if "account_no.json" not in os.listdir("data"):
        account_no = 1769261000
        with open("data/account_no.json", "w+") as f:
            json.dump(account_no, f)
        return account_no

    else:
        with open("data/account_no.json", "r") as f:
            account_no = json.load(f)
            account_no += 1
        with open("data/account_no.json", "w+") as f:
            json.dump(account_no, f)
        return account_no



def profile_id_creation():

    if "data" not in os.listdir():
        os.mkdir("data")
    if "profile_id.json" not in os.listdir("data"):
        profile_id = 1
        with open("data/profile_id.json", "w+") as f:
            json.dump(profile_id, f)

    else:
        with open("data/profile_id.json", "r") as f:
            profile_id = json.load(f)
            profile_id += 1
        with open("data/profile_id.json", "w+") as f:
            json.dump(profile_id, f)
    return profile_id