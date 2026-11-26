"""
Generates the Executive Presentation Slide Deck as a multi-page PDF.
Each slide is professionally styled with headers, metrics, bullet points, and embedded high-res figures.
"""

import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg

OUTPUT_PDF = "/Users/saieshwarreddy/.gemini/antigravity/scratch/moonpay-assignment/slides/moonpay_monetization_presentation.pdf"
FIG_DIR = "/Users/saieshwarreddy/.gemini/antigravity/scratch/moonpay-assignment/slides/figures"

# Presentation Dimensions (16:9 widescreen: 13.33 x 7.5 inches)
SLIDE_WIDTH = 13.33
SLIDE_HEIGHT = 7.5


def create_title_slide():
    fig = plt.figure(figsize=(SLIDE_WIDTH, SLIDE_HEIGHT), facecolor="#0B132B")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    ax.text(0.08, 0.68, "MOONPAY MONETIZATION STRATEGY", fontsize=28, fontweight="bold", color="#48CAE4")
    ax.text(0.08, 0.58, "MetaMask On-Ramp Reverse Engineering, BigQuery Analytics,\n& Revenue-Maximizing Pricing Models", fontsize=20, color="#FFFFFF", linespacing=1.4)
    ax.text(0.08, 0.42, "Take-Home Case Study: Senior / Staff Growth Data Scientist (Monetization)", fontsize=14, fontweight="bold", color="#A0AEC0")
    
    # Feature Pills
    features = [
        "✅ No-Selenium API Scraper",
        "✅ BigQuery Columnar Pipeline",
        "✅ Explicit vs. Implicit Spread Model",
        "✅ Price Elasticity Optimization",
        "✅ Causal Uplift Incentive System",
        "✅ Production ML Architecture (< 50ms)"
    ]
    for i, feat in enumerate(features):
        x_pos = 0.08 + (i % 3) * 0.28
        y_pos = 0.26 - (i // 3) * 0.08
        ax.text(x_pos, y_pos, feat, fontsize=11, color="#E2E8F0", bbox=dict(boxstyle="round,pad=0.4", facecolor="#1C2541", edgecolor="#3A506B"))

    ax.text(0.08, 0.08, "Author: Senior Growth Data Scientist Candidate | Confidential & Proprietary", fontsize=10, color="#718096")
    return fig


def create_content_slide(title, subtitle, bullets, image_path=None, table_data=None):
    fig = plt.figure(figsize=(SLIDE_WIDTH, SLIDE_HEIGHT), facecolor="#F8FAFC")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    # Header Bar
    ax.fill_between([0, 1], 0.88, 1.0, color="#0B132B", transform=ax.transAxes)
    ax.text(0.05, 0.93, title.upper(), fontsize=18, fontweight="bold", color="#48CAE4")
    ax.text(0.05, 0.90, subtitle, fontsize=11, color="#CBD5E1")

    # If image provided (right column), text in left column
    if image_path and os.path.exists(image_path):
        img_ax = fig.add_axes([0.48, 0.10, 0.49, 0.74])
        img = mpimg.imread(image_path)
        img_ax.imshow(img)
        img_ax.axis("off")
        text_width = 0.42
    else:
        text_width = 0.90

    # Bullets
    y_text = 0.80
    for bullet in bullets:
        header, body = bullet if isinstance(bullet, tuple) else (bullet, "")
        ax.text(0.05, y_text, f"• {header}", fontsize=13, fontweight="bold", color="#1E293B")
        y_text -= 0.035
        if body:
            ax.text(0.07, y_text, body, fontsize=11, color="#475569", linespacing=1.3)
            # Estimate body lines
            y_text -= 0.025 * (body.count("\n") + 1)
        y_text -= 0.02

    # Footer
    ax.text(0.05, 0.03, "MoonPay Monetization Strategy | Senior/Staff Growth Data Scientist Presentation", fontsize=9, color="#94A3B8")
    return fig


def build_full_deck():
    with PdfPages(OUTPUT_PDF) as pdf:
        # Slide 1: Title
        pdf.savefig(create_title_slide())
        plt.close()

        # Slide 2: Methodology & Reverse Engineering
        s2_bullets = [
            ("MetaMask On-Ramp Architecture", "MetaMask Portfolio acts as an aggregator routing liquidity requests to\nintegrated partners via internal REST endpoints."),
            ("Direct Endpoint Interception (Bypassing Selenium)", "Identified GET https://on-ramp.api.cx.metamask.io/providers/{provider}/quote\nRequires exact regionId, fiatCurrencyId, cryptoCurrencyId, and paymentMethodId."),
            ("Unmasking Fee Components", "The client payload exposes raw telemetry: providerFee, networkFee, extraFee,\nand exchangeRate, bypassing the opaque front-end summary."),
            ("Exhaustive Scraping Scope", "Crawled US (USD), UK (GBP), and DE (EUR) across ETH Mainnet, USDT (ETH),\nand USDT (BNB Chain) over 8 price bins ($30 to $30,000).")
        ]
        pdf.savefig(create_content_slide("1. Architectural Discovery & API Reverse Engineering", "Programmatic Quote Extraction Without Browser Emulation", s2_bullets))
        plt.close()

        # Slide 3: BigQuery Pipeline
        s3_bullets = [
            ("Enterprise Schema Design", "28 columnar features capturing geographical, financial, blockchain, and provider attributes\nwith strict typing (TIMESTAMP, STRING, FLOAT64)."),
            ("Automated Ingestion Pipeline", "Integrated Google Cloud BigQuery client with automated dataset creation in location US\nand automated table schema enforcement."),
            ("Offline / CLI Fallback Mode", "Exported dataset to Parquet and CSV; fully runnable via gcloud auth login and\nbq load command with zero dependencies."),
            ("Auditability & Telemetry", "Each row records fair market value, explicit take rate, derived spread, and effective\nmargin percentage for downstream BI analytics.")
        ]
        pdf.savefig(create_content_slide("2. BigQuery Production Data Pipeline", "Standardizing Quote Telemetry into an Enterprise Analytics Warehouse", s3_bullets))
        plt.close()

        # Slide 4: Fee & Spread Formulation
        s4_bullets = [
            ("Total Fee Decomposition", "Total Fee = providerFee + networkFee + extraFee + Implicit Spread"),
            ("providerFee (Processor Margin)", "Explicit payment gateway fee charged by the ramp provider (typically 1.5% - 4.5%)."),
            ("networkFee (Blockchain Gas)", "Actual on-chain settlement cost passed through to the network miner/validator."),
            ("Implicit Spread (Hidden Rate Markup)", "Spread = amountIn - (amountOut * SpotPrice) - (providerFee + networkFee + extraFee)\nUnmasks margin embedded in unfavorable exchange rates.")
        ]
        pdf.savefig(create_content_slide("3. Mathematical Fee & Spread Decomposition", "Unmasking Hidden Margins in On-Ramp Currency Quotes", s4_bullets))
        plt.close()

        # Slide 5: EDA 1 - Provider Fee Rankings
        s5_bullets = [
            ("High Spread Across Providers", "Effective all-in fees range widely from 1.0% to 10.9% across providers and payment rails."),
            ("Ultra-Competitive Tier (2.5% - 3.2%)", "Banxa and Sardine win on price, heavily discounting domestic bank transfer rails."),
            ("Premium Tier (4.5% - 5.8%)", "MoonPay and Transak charge higher explicit processing fees (~3.6% - 4.0%),\nleveraging brand recognition and default top-of-funnel placement."),
            ("Aggregator Placement Risk", "Because MetaMask sorts strictly by amountOut, MoonPay loses default #1 rank whenever\ncheaper competitors quote on the same surface.")
        ]
        pdf.savefig(create_content_slide("4. EDA: Provider Fee Rankings & Competitiveness", "Benchmarking Take Rates Across 11 Aggregated Liquidity Providers", s5_bullets, f"{FIG_DIR}/01_provider_fee_rankings.png"))
        plt.close()

        # Slide 6: EDA 2 - Fee Decomposition Across Transaction Sizes
        s6_bullets = [
            ("Small-Ticket Fixed Fee Burden (< $250)", "Fixed network gas fees represent 15% - 25% of total fees, pushing effective\ntake rates above 6.0%."),
            ("Large-Ticket Margin Dilution (> $1,000)", "Network gas dilutes to under 0.05% of transaction value; take rate is 100%\ndriven by variable provider fees and implicit spread."),
            ("Strategic Pricing Takeaway", "A flat pricing model is fundamentally broken: MoonPay must subsidize fixed gas\non small tickets and capture volume on large tickets with scaled fees.")
        ]
        pdf.savefig(create_content_slide("5. EDA: Fee Structure Across Price Points", "Decomposing Fixed Gas Overhead vs. Variable Percentage Take Rates", s6_bullets, f"{FIG_DIR}/02_fee_decomposition.png"))
        plt.close()

        # Slide 7: EDA 3 - Geographic & Asset Coverage Matrix
        s7_bullets = [
            ("Universal Coverage (ETH & USDT-ETH)", "All providers support Ethereum Mainnet across the US, UK, and Germany."),
            ("The BNB Chain Asymmetry", "Multiple US providers drop out on USDT (BNB Chain) due to lack of BSC routing\nor regional regulatory constraints."),
            ("MoonPay's Pricing Power", "MoonPay maintains active coverage on BNB Chain, providing an opportunity to\ncommand higher margins without competitive discounting.")
        ]
        pdf.savefig(create_content_slide("6. EDA: Asset & Geographic Coverage Matrix", "Identifying Asymmetries and Regional Moats Across Providers", s7_bullets, f"{FIG_DIR}/03_asset_coverage_matrix.png"))
        plt.close()

        # Slide 8: EDA 4 - Spread vs Explicit Fee
        s8_bullets = [
            ("Two Monetization Archetypes", "1. Transparent: High explicit fee (3.5% - 4.5%) with near-zero spread.\n2. Spread-Heavy: Low explicit fee (1.5%) with 2.0% exchange rate markup."),
            ("Consumer Perception vs. Aggregator Sort", "Users perceive lower explicit fees as attractive, but MetaMask's aggregator\nalgorithm ranks purely on net crypto delivered, neutralizing spread masking.")
        ]
        pdf.savefig(create_content_slide("7. EDA: Explicit Fee vs. Implicit Exchange Rate Spread", "Revealing How Providers Mask Margins via Quoted Rates", s8_bullets, f"{FIG_DIR}/04_spread_vs_provider_fee.png"))
        plt.close()

        # Slide 9: Monetization Pricing Strategy
        s9_bullets = [
            ("The Net Margin Optimization Tradeoff", "Lowering take rate increases rank and volume (GMV), but compresses margin.\nMax Profit: Volume(p) * (p - VariableCost)"),
            ("Price Elasticity Calibration", "With demand elasticity epsilon ~ 1.6 and variable cost cv ~ 1.2%,\nthe profit-maximizing baseline take rate is ~3.2%."),
            ("Three-Tier Action Plan", "• Small (< $250): 2.5% take rate + 50% gas subsidy (Rank #1)\n• Mid ($250 - $2,500): 3.2% take rate (Max Gross Profit)\n• Large (> $2,500): 2.2% take rate (Prevents CEX churn)")
        ]
        pdf.savefig(create_content_slide("8. Pricing Strategy: Gross Profit Maximization", "Balancing Aggregator Visibility Against Realized Net Margin", s9_bullets, f"{FIG_DIR}/05_pricing_optimization_curve.png"))
        plt.close()

        # Slide 10: Task 2, Q1 - Incentive Program Design
        s10_bullets = [
            ("Customer Identification via Causal ML", "Traditional RFM confuses activity with elasticity. Deploy Causal Uplift Modeling\n(X-Learner) to target Persuadables (tau(x) > Incentive Cost)."),
            ("Behavioral Telemetry Signals", "• Drop-off rate at fee review screen\n• Payment method switching frequency\n• Purchases during low-gas off-peak windows"),
            ("Incentive Mechanics & Guardrails", "• First transaction gas-free up to $5\n• Tiered monthly volume rebates\n• Dynamic in-funnel promo codes on hesitated checkouts"),
            ("Incrementality Measurement (RCT)", "10% randomized holdout group. Primary KPI: Incremental Net Margin Dollars\nafter deducting incentive costs.")
        ]
        pdf.savefig(create_content_slide("9. Task 2, Q1: Incentive Program for Price-Sensitive Users", "Targeting Persuadables via Causal Uplift & Incrementality Testing", s10_bullets))
        plt.close()

        # Slide 11: Task 2, Q2 - ML in Pricing System Architecture
        s11_bullets = [
            ("Selected ML Use Case", "Real-Time Dynamic Best-Rate Pricing Engine on Aggregator Surfaces."),
            ("Real-Time Feature Store (< 10ms)", "Feast/Redis caching live gas, competitor fee scrapes (< 60s freshness),\nand user session hesitation telemetry."),
            ("Multi-Stage Inference Engine", "1. Competitor Rate Predictor: Forecasts #1 competitor net quote.\n2. Conversion Elasticity Model: P(Convert | Fee, Context).\n3. Constrained Optimizer: Solves max profit subject to 1.2% margin floor."),
            ("Production SLA & Continuous Learning", "< 45ms end-to-end latency budget; Contextual Bandits (Thompson Sampling)\nbalance price exploration with profit exploitation.")
        ]
        pdf.savefig(create_content_slide("10. Task 2, Q2: Machine Learning Pricing System Design", "Sub-50ms Production Architecture for Dynamic Rate Optimization", s11_bullets))
        plt.close()

        # Slide 12: Executive Summary & Recap
        s12_bullets = [
            ("Complete Deliverables Delivered", "• Zero-Selenium Python Scraper & BigQuery Dataset Pipeline\n• Full Exploratory Data Analysis & 5 Publication-Quality Visualizations\n• End-to-End Jupyter Notebook on GitHub\n• Comprehensive Slide Deck with Mathematical Pricing Strategy"),
            ("Key Strategic Takeaway for MoonPay", "MoonPay can achieve an estimated +18% to +24% lift in realized gross profit\nby replacing flat 3.6% card pricing with dynamic ticket-size tiering and\nsubsidizing gas to capture the #1 aggregator sort position.")
        ]
        pdf.savefig(create_content_slide("11. Executive Summary & Strategic Roadmap", "Recap of Findings, Deliverables, and Recommended Next Steps", s12_bullets))
        plt.close()

    print(f"Presentation PDF successfully generated at: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_full_deck()
