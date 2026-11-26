# MoonPay Case Study: Senior / Staff Growth Data Scientist (Monetization)

An end-to-end technical, quantitative, and strategic pricing analysis investigating the MetaMask fiat on-ramp aggregator ecosystem, developing BigQuery pipelines, decomposing explicit fees and implicit currency rate spreads, and formulating profit-maximizing monetization models.

---

## 📁 Repository Structure

```
moonpay-assignment/
├── notebooks/
│   └── moonpay_analysis.ipynb          # Main Python Jupyter Notebook (End-to-End)
├── slides/
│   ├── moonpay_monetization_presentation.pdf   # Executive Presentation Slide Deck (12 Slides)
│   ├── PRESENTATION_SLIDES.md                  # Markdown Source for Presentation
│   └── figures/                                # High-Resolution Visualizations (DPI 300)
│       ├── 01_provider_fee_rankings.png
│       ├── 02_fee_decomposition.png
│       ├── 03_asset_coverage_matrix.png
│       ├── 04_spread_vs_provider_fee.png
│       └── 05_pricing_optimization_curve.png
├── src/
│   ├── scraper.py                      # Production API crawler (Zero-browser automation)
│   ├── bigquery_loader.py              # BigQuery schema & dataset ingestion pipeline
│   └── generate_charts.py              # Visual analytics & figure generation engine
├── data/
│   ├── metamask_provider_quotes.csv    # Extracted quotes dataset (CSV)
│   └── metamask_provider_quotes.parquet # Extracted quotes dataset (Parquet)
├── requirements.txt                    # Python dependencies
└── README.md                           # Documentation & execution guide
```

---

## 🚀 Quickstart Guide

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/saieshwarreddy05/moonpay-monetization-case-study.git
cd moonpay-monetization-case-study

# Create virtual environment & install requirements
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Scraper Bot
```bash
python3 src/scraper.py
```

### 3. Generate Analytical Figures
```bash
python3 src/generate_charts.py
```

### 4. Build Presentation Deck
```bash
python3 build_html_presentation.py
```

### 5. Launch Jupyter Notebook
```bash
jupyter notebook notebooks/moonpay_analysis.ipynb
```

---

## 🔑 Key Methodological Insights

### 1. Reverse-Engineering MetaMask Portfolio (No Selenium / Puppeteer)
Rather than fragile browser emulation, the bot intercepts MetaMask's underlying REST aggregation gateway:
* **Quote Route:** `GET https://on-ramp.api.cx.metamask.io/providers/{provider}/quote`
* **Metadata Cache:** `GET https://on-ramp-cache.api.cx.metamask.io/regions/{regionId}/light`
* **Fee Granularity:** Extracts explicit `providerFee`, `networkFee`, `extraFee`, and quotes directly from response payloads.

### 2. Unmasking the Implicit Spread
The prompt notes that explicit fees do not add up to the total fiat-to-crypto delta. We mathematically isolate the implicit spread:

$$\text{Implicit Spread} = \text{amountIn} - (\text{amountOut} \times \text{SpotPrice}) - (\text{providerFee} + \text{networkFee} + \text{extraFee})$$

### 3. Monetization Pricing Optimization
We model retail crypto on-ramp demand using an iso-elastic demand curve ($\epsilon \approx 1.6$). The gross-profit-maximizing take rate is derived as:

$$p^* = \frac{\epsilon}{\epsilon - 1} \cdot c_v \approx 3.2\%$$

With three distinct operational tiers:
* **Small Tickets (< $250):** 2.5% take rate + 50% gas subsidy (wins #1 rank).
* **Mid Tickets ($250 - $2,500):** 3.2% take rate (profit sweet spot).
* **Large Tickets (> $2,500):** 2.2% take rate (prevents CEX churn).

---

## 📊 BigQuery Data Warehouse Integration

To load the processed quotes table into your free Google Cloud BigQuery sandbox:

```bash
# Authenticate with your Gmail GCP account
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID

# Create the BigQuery dataset
bq --location=US mk --dataset YOUR_GCP_PROJECT_ID:onramp_monetization

# Ingest data
bq load --autodetect --source_format=CSV \
    YOUR_GCP_PROJECT_ID:onramp_monetization.metamask_provider_quotes \
    data/metamask_provider_quotes.csv
```

---

## 🎯 Task 2 Conceptual Summaries

* **Q1 (Incentive Program for Price-Sensitive Users):** Formulates a Causal Uplift Model ($X$-Learner) to target only *Persuadables*, filtering out inelastic users to avoid margin cannibalization. Evaluated via a 10% randomized holdout (RCT) on incremental gross margin dollars.
* **Q2 (ML in Pricing Architecture):** Designs a sub-50ms real-time dynamic pricing engine consisting of a Feast/Redis feature store, LightGBM competitor rate forecasting, a conversion probability model, a constrained mathematical optimizer, and Contextual Bandits (Thompson Sampling).
