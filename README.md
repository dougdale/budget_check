# budget_check
Check monthly spending averages from YNAB against desired budget values

## Required Python Packages
- pandas
- openpyxl

## Configuration Files
At least two configuration files are required.

### config.yaml
This YAML file contains your YNAB API token and budget ID. See the [YNAB API Documentation](https://api.ynab.com) for details.

```yaml
ynab_api_token: '<token>'
ynab_budget_id: '<budget ID>'
```

### Budget File
This JSON file contains a list of your budget categories and the monthly budget target as in the example below.

```json
{
  "budget": {
    "Inflow: Ready to Assign": 10450,
    "Groceries": 600,
    "Income Tax": 1200,
    "Mortgage": 1400
  }
}
```