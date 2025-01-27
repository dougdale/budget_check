#!/usr/bin/env python3
import requests
import yaml
import datetime
from dateutil.relativedelta import relativedelta

def get_transactions(api_token, budget_id, start_date):
    url = f'https://api.youneedabudget.com/v1/budgets/{budget_id}/transactions'
    headers = {
        'Authorization': f'Bearer {api_token}'
    }
    params = {
        'since_date': start_date,
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()['data']['transactions']

# Calculate the average amount spent per month for each category
# We pass in the explicit end date so we don't have any "date math" issues and
# n_months in case there are categories with no transactions in the last n
# months
def calculate_monthly_average_spent(transactions, last_day, n_months):
    category_totals = {}

    def update_totals(category_name, amount):
        if category_name not in category_totals:
            category_totals[category_name] =  0

        category_totals[category_name] += amount

    # Get category totals for each transaction, taking into account subtransactions
    for transaction in transactions:
        date = datetime.datetime.strptime(transaction['date'], '%Y-%m-%d')
        if date > last_day:
            continue

        if len(transaction['subtransactions']) == 0:
            update_totals(transaction['category_name'], transaction['amount'])
        else:
            for subtransaction in transaction['subtransactions']:
                update_totals(subtransaction['category_name'], subtransaction['amount'])

    category_averages = {}
    for category_name, total in category_totals.items():
        category_averages[category_name] = total / (n_months * 1000)

    return category_averages

def get_last_day_of_previous_month():
    today = datetime.date.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
    return datetime.datetime.combine(last_day_of_previous_month, datetime.time(23, 59, 59))

def get_first_day_of_n_months_ago(n):
    today = datetime.date.today()
    first_day_of_n_months_ago = (today.replace(day=1) - relativedelta(months=n)).replace(day=1)
    return datetime.datetime.combine(first_day_of_n_months_ago, datetime.time(0, 0, 0))

def read_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_ynab_spending_averages(n_months):
    config = read_config('config.yaml')
    ynab_api_token = config['ynab_api_token']
    ynab_budget_id = config['ynab_budget_id']
    last_day_of_previous_month = get_last_day_of_previous_month()
    first_day_of_n_months_ago = get_first_day_of_n_months_ago(n_months)
    transactions = get_transactions(ynab_api_token, ynab_budget_id, first_day_of_n_months_ago)
    return calculate_monthly_average_spent(transactions, last_day_of_previous_month, n_months)

if __name__ == '__main__':
    data = get_ynab_spending_averages(12)

    for category, average in data.items():
        print(f'{category}: {average:.2f}')
