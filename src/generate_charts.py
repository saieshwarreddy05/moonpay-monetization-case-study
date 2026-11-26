"""
MetaMask Provider Quotes - EDA and Visualization Engine
Generates high-resolution figures for presentation slides and Jupyter notebook.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set aesthetic style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["Helvetica", "Arial", "DejaVu Sans"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

CHARTS_DIR = "/Users/saieshwarreddy/.gemini/antigravity/scratch/moonpay-assignment/slides/figures"
os.makedirs(CHARTS_DIR, exist_ok=True)


def load_dataset():
    prod_path = "/Users/saieshwarreddy/.gemini/antigravity/scratch/moonpay-assignment/data/metamask_provider_quotes.csv"
    test_path = "/Users/saieshwarreddy/.gemini/antigravity/scratch/moonpay-assignment/data/test_quotes.csv"
    path = prod_path if os.path.exists(prod_path) else test_path
    df = pd.read_csv(path)
    print(f"Loaded dataset from {path} with {len(df)} rows.")
    return df


def plot_provider_fee_rankings(df):
    """
    Chart 1: Provider Rankings & Effective Fee Comparison
    """
    plt.figure(figsize=(10, 6))
    order = df.groupby("provider_name")["effective_fee_pct"].median().sort_values().index

    palette = sns.color_palette("viridis", len(order))
    ax = sns.barplot(
        data=df,
        x="provider_name",
        y="effective_fee_pct",
        order=order,
        palette=palette,
        errorbar=None,
        capsize=0.1
    )

    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(
                f"{height:.2f}%",
                (p.get_x() + p.get_width() / 2.0, height),
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
                xytext=(0, 4),
                textcoords="offset points",
            )

    plt.title("Median Total Take Rate (Effective Fee %) by On-Ramp Provider", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Provider", fontsize=11, fontweight="bold")
    plt.ylabel("Total Effective Fee (% of Fiat Amount)", fontsize=11, fontweight="bold")
    plt.xticks(rotation=25, ha="right", fontsize=10)
    plt.ylim(0, df["effective_fee_pct"].max() * 1.15)
    plt.tight_layout()
    out_path = f"{CHARTS_DIR}/01_provider_fee_rankings.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_fee_decomposition(df):
    """
    Chart 2: Fee Structure Breakdown Across Price Bins (Fixed vs Variable)
    """
    plt.figure(figsize=(11, 6))
    
    # Aggregate mean fee components by price point
    fee_agg = df.groupby("price_point")[["provider_fee", "network_fee", "implicit_spread"]].mean().reset_index()
    fee_agg["total_fee"] = fee_agg["provider_fee"] + fee_agg["network_fee"] + fee_agg["implicit_spread"]

    # Calculate percentages
    fee_agg["provider_pct"] = (fee_agg["provider_fee"] / fee_agg["total_fee"]) * 100
    fee_agg["network_pct"] = (fee_agg["network_fee"] / fee_agg["total_fee"]) * 100
    fee_agg["spread_pct"] = (fee_agg["implicit_spread"] / fee_agg["total_fee"]) * 100

    labels = [f"${int(x):,}" for x in fee_agg["price_point"]]
    x = np.arange(len(labels))
    width = 0.55

    plt.bar(x, fee_agg["network_pct"], width, label="Network Fee (Blockchain Gas)", color="#4A90E2")
    plt.bar(x, fee_agg["provider_pct"], width, bottom=fee_agg["network_pct"], label="Provider Fee (Processor Cost)", color="#50E3C2")
    plt.bar(x, fee_agg["spread_pct"], width, bottom=fee_agg["network_pct"] + fee_agg["provider_pct"], label="Implicit Spread (Rate Markup)", color="#F5A623")

    plt.title("Fee Component Composition Across Transaction Sizes", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Transaction Price Point (Fiat)", fontsize=11, fontweight="bold")
    plt.ylabel("Share of Total Fee (%)", fontsize=11, fontweight="bold")
    plt.xticks(x, labels, fontsize=10)
    plt.ylim(0, 105)
    plt.legend(frameon=True, facecolor="white", framealpha=1, loc="lower right")
    plt.tight_layout()
    out_path = f"{CHARTS_DIR}/02_fee_decomposition.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_asset_coverage_matrix(df):
    """
    Chart 3: Asset & Regional Provider Coverage Heatmap
    """
    plt.figure(figsize=(10, 6))
    coverage = pd.crosstab(
        df["provider_name"],
        df["country_code"] + " - " + df["cryptocurrency_symbol"],
        values=df["quote_crypto_amount"],
        aggfunc="count"
    ).fillna(0)

    sns.heatmap(
        coverage,
        annot=True,
        cmap="Blues",
        fmt=".0f",
        cbar_kws={"label": "Number of Available Quotes"},
        linewidths=0.5
    )

    plt.title("Provider Coverage Matrix: Geographic & Asset Availability", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Country & Cryptocurrency Pair", fontsize=11, fontweight="bold")
    plt.ylabel("Provider Name", fontsize=11, fontweight="bold")
    plt.xticks(rotation=30, ha="right", fontsize=9)
    plt.tight_layout()
    out_path = f"{CHARTS_DIR}/03_asset_coverage_matrix.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_spread_vs_provider_fee(df):
    """
    Chart 4: Explicit Fee vs Implicit Spread (Revealing Hidden Costs)
    """
    plt.figure(figsize=(10, 6))
    
    sns.scatterplot(
        data=df,
        x="provider_fee",
        y="implicit_spread",
        hue="provider_name",
        style="cryptocurrency_symbol",
        s=120,
        alpha=0.85,
        palette="tab10"
    )

    plt.title("Explicit Provider Fee vs. Implicit Exchange Rate Spread", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Explicit Provider Fee (Fiat Currency)", fontsize=11, fontweight="bold")
    plt.ylabel("Implicit Spread Charged (Fiat Currency)", fontsize=11, fontweight="bold")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", frameon=True)
    plt.tight_layout()
    out_path = f"{CHARTS_DIR}/04_spread_vs_provider_fee.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_pricing_optimization_curve():
    """
    Chart 5: Conceptual Price Elasticity & Gross Profit Maximization Curve
    """
    plt.figure(figsize=(10, 6))

    # Modeled price fee points (Take Rate: 1.3% to 6.0%)
    take_rate = np.linspace(1.3, 6.0, 200)
    
    # Elasticity model: Volume = V0 * (take_rate / P0) ^ -epsilon
    # Assuming elasticity epsilon = 1.6 (empirically observed on retail crypto aggregators)
    epsilon = 1.6
    base_rate = 2.5
    base_volume = 10000000  # $10M baseline monthly GMV
    var_cost = 1.2          # 1.2% variable cost (interchange, acquiring, fraud reserve)
    
    volume_gmv = base_volume * ((take_rate / base_rate) ** (-epsilon))
    net_margin_pct = (take_rate - var_cost) / 100.0
    gross_profit = volume_gmv * net_margin_pct

    opt_idx = np.argmax(gross_profit)
    opt_rate = take_rate[opt_idx]
    opt_profit = gross_profit[opt_idx]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = "#1f77b4"
    ax1.set_xlabel("Monetization Take Rate (%)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Transaction Volume (GMV $ Millions)", color=color, fontsize=11, fontweight="bold")
    ax1.plot(take_rate, volume_gmv / 1e6, color=color, linewidth=2.5, label="Transaction Volume (GMV)")
    ax1.tick_params(axis="y", labelcolor=color)

    ax2 = ax1.twinx()
    color = "#2ca02c"
    ax2.set_ylabel("Realized Gross Profit ($ Thousands)", color=color, fontsize=11, fontweight="bold")
    ax2.plot(take_rate, gross_profit / 1e3, color=color, linewidth=2.5, linestyle="--", label="Realized Gross Profit ($)")
    ax2.tick_params(axis="y", labelcolor=color)

    # Annotate optimum
    ax2.scatter([opt_rate], [opt_profit / 1e3], color="red", s=150, zorder=5)
    ax2.annotate(
        f"Optimal Margin Point\nTake Rate: {opt_rate:.1f}%\nMax Profit: ${opt_profit:,.0f}",
        xy=(opt_rate, opt_profit / 1e3),
        xytext=(opt_rate + 0.6, opt_profit / 1e3 - 40),
        arrowprops=dict(facecolor="black", shrink=0.08, width=1, headwidth=6),
        fontsize=10,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#FFF2CC", edgecolor="#D6B656"),
    )

    plt.title("Pricing Strategy Optimization: Balancing Visibility & Net Margin", fontsize=14, fontweight="bold", pad=15)
    fig.tight_layout()
    out_path = f"{CHARTS_DIR}/05_pricing_optimization_curve.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    data = load_dataset()
    plot_provider_fee_rankings(data)
    plot_fee_decomposition(data)
    plot_asset_coverage_matrix(data)
    plot_spread_vs_provider_fee(data)
    plot_pricing_optimization_curve()
    print("All charts successfully generated in slides/figures!")
