# ecommerce-conversion-optimization

E-commerce conversion optimization project for data analysis, SQL exploration, modeling scripts, visualization outputs, and Coze workflow assets.

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
- `coze/`: Coze prompts, configs, or workflow files.

## Project Goals
- Load Kaggle e-commerce dataset into MySQL
- Build user-level features
- Train a logistic regression model
- Simulate targeted marketing uplift
- Generate business insights with Coze
