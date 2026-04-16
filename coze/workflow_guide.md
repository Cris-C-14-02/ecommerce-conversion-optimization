# Coze Workflow Guide

## Goal

Turn analysis outputs from SQL and Python into a repeatable Coze workflow that generates business-ready insight summaries.

## Suggested Flow

1. Run SQL scripts to produce funnel and user path metrics.
2. Run `scripts/model.py` to generate:
   - `outputs/results/model_summary.json`
   - `outputs/results/user_segment_summary.csv`
   - `outputs/results/top_remarketing_targets.csv`
   - `outputs/results/ab_test_group_summary.csv`
3. Merge the key results into a single JSON payload that matches `coze/insight_schema.json`.
4. Feed that payload into Coze together with `coze/prompt_template.md`.
5. Ask Coze to return a business insight report for marketing or product stakeholders.

## Recommended Coze Nodes

- Input node: structured JSON metrics from SQL and modeling outputs
- LLM node: prompt from `coze/prompt_template.md`
- Formatter node: enforce section headers for business output
- Optional router node: generate separate summaries for product, CRM, or leadership audiences

## Suggested Input Mapping

- Funnel metrics:
  - `view_users`
  - `cart_users`
  - `purchase_users`
  - `view_to_cart_rate`
  - `cart_to_purchase_rate`
- User path metrics:
  - `only_viewed_users`
  - `cart_not_purchase_users`
  - `anomaly_note`
- Modeling outputs:
  - `model_metrics`
  - `segment_summary`
  - `top_target_users`
- Experiment outputs:
  - `ab_test_summary`

## Example Business Questions For Coze

- Where is the biggest conversion bottleneck right now?
- Which users should receive remarketing first?
- What strategy is most likely to improve conversion in the short term?
- What uplift can the business expect if the treatment works as simulated?

## Final Deliverable Idea

Use Coze to generate:

- a one-paragraph executive summary
- a short action plan
- a segment recommendation
- an expected uplift statement
- a risk note about tracking anomalies or model assumptions
