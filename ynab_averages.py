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

def get_categories(api_token, budget_id):
    url = f'https://api.youneedabudget.com/v1/budgets/{budget_id}/categories'
    headers = {
        'Authorization': f'Bearer {api_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    categories = response.json()['data']['category_groups']
    category_map = {}
    for group in categories:
        for category in group['categories']:
            category_map[category['id']] = category['name']
    return category_map

# Calculate the average amount spent per month for each category
# We pass in the explicit end date so we don't have any "date math" issues and
# n_months in case there are categories with no transactions in the last n
# months
def calculate_monthly_average_spent(transactions, last_day, n_months):
    category_totals = {}

    for transaction in transactions:
        category_id = transaction['category_id']
        amount = transaction['amount']

        date = datetime.datetime.strptime(transaction['date'], '%Y-%m-%d')
        if date > last_day:
            continue

        month = date.strftime('%Y-%m')

        if category_id not in category_totals:
            category_totals[category_id] = {}

        if month not in category_totals[category_id]:
            category_totals[category_id][month] = 0

        category_totals[category_id][month] += amount

    print(category_totals)
    category_averages = {category_id: sum(month_totals.values()) / n_months for category_id, month_totals in category_totals.items()}
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

def main():
    config = read_config('config.yaml')
    ynab_api_token = config['ynab_api_token']
    ynab_budget_id = config['ynab_budget_id']
    n_months = 12
    last_day_of_previous_month = get_last_day_of_previous_month()
    first_day_of_n_months_ago = get_first_day_of_n_months_ago(n_months)
    transactions = get_transactions(ynab_api_token, ynab_budget_id, first_day_of_n_months_ago)
    category_map = get_categories(ynab_api_token, ynab_budget_id)
    averages = calculate_monthly_average_spent(transactions, last_day_of_previous_month, n_months)

    for category_id, average in averages.items():
        category_name = category_map.get(category_id, 'Unknown Category')
        print(f'Category: {category_name}, Monthly Average Spent: {average / 1000:.2f}')

if __name__ == '__main__':
    main()