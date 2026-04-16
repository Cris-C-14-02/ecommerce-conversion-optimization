# ecommerce-conversion-optimization

E-commerce conversion optimization project for data analysis, SQL exploration, modeling scripts, and visualization outputs, with a reserved interface for optional Coze integration.

A small sample (100 rows) of the engineered user-level dataset is included for demonstration purposes. The full dataset is stored in MySQL and used for modeling.

## Project Structure

```text
ecommerce-conversion-optimization/
├── data/
│   ├── raw/
│   └── processed/
├── sql/
├── scripts/
├── outputs/
│   ├── figures/
│   └── results/
├── notebooks/
├── coze/
├── README.md
├── requirements.txt
└── .gitignore
```

## Folder Guide

- `data/raw/`: original source data files.
- `data/processed/`: cleaned or transformed datasets.
- `sql/`: SQL queries and analysis scripts.
- `scripts/`: Python scripts for ETL, analysis, and automation.
- `outputs/figures/`: charts and visual assets.
- `outputs/results/`: exported metrics, tables, and model results.
- `notebooks/`: exploratory analysis notebooks.
- `coze/`: reserved templates and interface files for optional Coze integration.

## Project Goals
- Load Kaggle e-commerce dataset into MySQL
- Build user-level features
- Train a logistic regression model
- Simulate targeted marketing uplift
- Preserve an interface for optional AI insight generation

## Current Workflow

```text
events_raw
-> SQL data checks
-> funnel analysis
-> user path analysis
-> feature engineering
-> logistic regression scoring
-> A/B test simulation
-> optional Coze interface
```

## Modeling Output

The main modeling script is `scripts/model.py`.

It will:

- connect to MySQL and read `user_features`
- train a logistic regression model for `label_purchase`
- generate `pred_prob` for each user
- create user segments from low to very high intent
- build a remarketing target list
- simulate treatment vs control uplift for a marketing campaign using conservative baseline assumptions
- export results to `outputs/results/`

### Default features

- `view_count`
- `cart_count`
- `has_viewed`
- `has_carted`
- `view_to_cart_rate`

Purchase-derived fields such as `purchase_count` and `cart_to_purchase_rate` remain useful for descriptive analysis, but they are excluded from model training to avoid target leakage.

### Output files

- `outputs/results/model_coefficients.csv`
- `outputs/results/user_scoring_results.csv`
- `outputs/results/user_segment_summary.csv`
- `outputs/results/top_remarketing_targets.csv`
- `outputs/results/ab_test_candidates.csv`
- `outputs/results/ab_test_group_summary.csv`
- `outputs/results/model_summary.json`

## How To Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set MySQL credentials in your shell before running the scripts:

```powershell
$env:MYSQL_USERNAME="your_username"
$env:MYSQL_PASSWORD="your_password"
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_DATABASE="ecommerce"
```

3. Run the modeling pipeline:

```bash
python scripts/model.py
```

The same environment variables are used by `scripts/load_to_mysql.py`.

## Coze Interface

The `coze/` folder now includes:

- `prompt_template.md`: optional prompt template for business insight generation
- `insight_schema.json`: example structured payload for external AI tools
- `workflow_guide.md`: reference for connecting SQL + modeling outputs into Coze if needed

These files are kept as a reserved interface layer. The core project scope remains:

```text
data analysis -> model -> strategy simulation
```

If needed later, the reserved Coze interface can be used to convert structured outputs into business-facing narrative summaries.
