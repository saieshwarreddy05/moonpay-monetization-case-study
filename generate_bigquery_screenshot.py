"""
Generates a pixel-perfect, high-resolution Google Cloud BigQuery Console mockup screenshot
for embedding in presentation slides and documentation.
"""

from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os

OUTPUT_PATH = "/Users/saieshwarreddy/.gemini/antigravity/scratch/moonpay-assignment/slides/figures/bigquery_console_screenshot.png"
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# 1920 x 1080 Full HD image
WIDTH, HEIGHT = 1920, 1080
img = Image.new("RGB", (WIDTH, HEIGHT), color="#F8FAFD")
draw = ImageDraw.Draw(img)

# Try loading system sans fonts
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/SFPro.ttf", 20)
    font_header = ImageFont.truetype("/System/Library/Fonts/SFPro.ttf", 16)
    font_bold = ImageFont.truetype("/System/Library/Fonts/SFPro-Bold.ttf", 14)
    font_body = ImageFont.truetype("/System/Library/Fonts/SFPro.ttf", 13)
    font_code = ImageFont.truetype("/System/Library/Fonts/SFMono-Regular.otf", 13)
except Exception:
    font_title = ImageFont.load_default()
    font_header = font_title
    font_bold = font_title
    font_body = font_title
    font_code = font_title

# 1. Top GCP Nav Bar (Height 56px)
draw.rectangle([(0, 0), (WIDTH, 56)], fill="#1A73E8")
draw.text((24, 16), "Google Cloud", fill="#FFFFFF", font=font_title)
draw.text((160, 18), "BigQuery Studio", fill="#E8F0FE", font=font_header)

# Project Selector Pill
draw.rectangle([(320, 10), (620, 46)], fill="#1765CC", outline="#4285F4", width=1)
draw.text((340, 18), "Project: moonpay-growth-analytics", fill="#FFFFFF", font=font_body)

# Search Bar in Header
draw.rectangle([(660, 10), (1300, 46)], fill="#FFFFFF", outline="#D2E3FC", width=1)
draw.text((680, 18), "Search resources, tables, and datasets...", fill="#70757A", font=font_body)

# User / Avatar Icon
draw.ellipse([(1850, 12), (1884, 46)], fill="#EA4335")
draw.text((1862, 17), "M", fill="#FFFFFF", font=font_bold)

# 2. Left Explorer Navigation Pane (Width 320px)
draw.rectangle([(0, 56), (320, HEIGHT)], fill="#FFFFFF", outline="#E0E0E0", width=1)
draw.text((20, 75), "Explorer", fill="#202124", font=font_bold)

# Project Tree
draw.text((24, 115), "▼  moonpay-growth-analytics", fill="#1A73E8", font=font_bold)
draw.text((44, 145), "▼  onramp_monetization (dataset: US)", fill="#3C4043", font=font_body)
draw.rectangle([(55, 172), (310, 202)], fill="#E8F0FE")
draw.text((64, 178), "▤  metamask_provider_quotes", fill="#1A73E8", font=font_bold)
draw.text((44, 215), "▷  pricing_elasticity_models", fill="#5F6368", font=font_body)
draw.text((44, 245), "▷  user_uplift_segments", fill="#5F6368", font=font_body)

# 3. Main Workspace Tab & Action Bar
draw.rectangle([(320, 56), (WIDTH, 105)], fill="#FFFFFF", outline="#E0E0E0", width=1)
draw.text((345, 72), "metamask_provider_quotes", fill="#202124", font=font_title)
draw.text((630, 75), "Table in dataset onramp_monetization", fill="#5F6368", font=font_body)

# Sub Tabs
tabs = [("Schema", 345), ("Details", 445), ("Preview", 545), ("Lineage", 645)]
for t_name, x_pos in tabs:
    if t_name == "Preview":
        draw.text((x_pos, 115), t_name, fill="#1A73E8", font=font_bold)
        draw.rectangle([(x_pos - 8, 138), (x_pos + 65, 141)], fill="#1A73E8")
    else:
        draw.text((x_pos, 115), t_name, fill="#5F6368", font=font_body)

# 4. SQL Query Panel Preview
draw.rectangle([(340, 155), (WIDTH - 40, 275)], fill="#202124", outline="#3C4043", width=1)
draw.text((360, 170), "-- BigQuery SQL: Take Rate & Spread Benchmark across Surface Providers", fill="#9AA0A6", font=font_code)
sql_code = (
    "SELECT\n"
    "    country_code, cryptocurrency_symbol, provider_name,\n"
    "    COUNT(1) as total_quotes,\n"
    "    ROUND(AVG(provider_fee), 2) as avg_provider_fee,\n"
    "    ROUND(AVG(implicit_spread), 2) as avg_spread,\n"
    "    ROUND(AVG(effective_fee_pct), 2) as avg_effective_take_rate_pct\n"
    "FROM `moonpay-growth-analytics.onramp_monetization.metamask_provider_quotes`\n"
    "GROUP BY 1, 2, 3 ORDER BY avg_effective_take_rate_pct ASC;"
)
y_sql = 195
for line in sql_code.split("\n"):
    draw.text((360, y_sql), line, fill="#8AB4F8" if "SELECT" in line or "FROM" in line or "GROUP" in line else "#CEEAD6", font=font_code)
    y_sql += 16

# Run Query Button
draw.rectangle([(WIDTH - 180, 170), (WIDTH - 60, 205)], fill="#1A73E8")
draw.text((WIDTH - 155, 178), "▶  RUN", fill="#FFFFFF", font=font_bold)

# 5. Table Preview Results Grid
grid_top = 295
draw.rectangle([(340, grid_top), (WIDTH - 40, HEIGHT - 40)], fill="#FFFFFF", outline="#E0E0E0", width=1)

# Table Header
headers = [
    ("Row", 50),
    ("scraped_timestamp", 180),
    ("country", 70),
    ("fiat", 60),
    ("crypto", 70),
    ("price_point", 100),
    ("provider_name", 130),
    ("quote_crypto", 130),
    ("provider_fee", 100),
    ("network_fee", 100),
    ("implicit_spread", 120),
    ("total_fee", 90),
    ("effective_fee_pct", 130),
]

x_curr = 350
draw.rectangle([(340, grid_top), (WIDTH - 40, grid_top + 38)], fill="#F1F3F4")
for h_name, h_width in headers:
    draw.text((x_curr, grid_top + 10), h_name, fill="#202124", font=font_bold)
    x_curr += h_width

# Load sample data from CSV
df = pd.read_csv("/Users/saieshwarreddy/.gemini/antigravity/scratch/moonpay-assignment/data/metamask_provider_quotes.csv")
y_row = grid_top + 45
row_idx = 1

for _, r in df.head(15).iterrows():
    fill_bg = "#FFFFFF" if row_idx % 2 != 0 else "#F8FAFD"
    draw.rectangle([(341, y_row - 4), (WIDTH - 41, y_row + 24)], fill=fill_bg)
    
    x_curr = 350
    vals = [
        str(row_idx),
        str(r.get("scraped_timestamp", ""))[:19],
        str(r.get("country_code", "")),
        str(r.get("fiat_currency", "")),
        str(r.get("cryptocurrency_symbol", "")),
        f"${float(r.get('price_point', 0)):,.2f}",
        str(r.get("provider_name", "")),
        f"{float(r.get('quote_crypto_amount', 0)):.6f}",
        f"${float(r.get('provider_fee', 0)):.2f}",
        f"${float(r.get('network_fee', 0)):.2f}",
        f"${float(r.get('implicit_spread', 0)):.2f}",
        f"${float(r.get('total_fee', 0)):.2f}",
        f"{float(r.get('effective_fee_pct', 0)):.2f}%",
    ]
    for val, (_, h_width) in zip(vals, headers):
        draw.text((x_curr, y_row), val, fill="#3C4043", font=font_body)
        x_curr += h_width
    
    y_row += 28
    row_idx += 1

img.save(OUTPUT_PATH, "PNG", quality=95)
print(f"Generated BigQuery console screenshot at: {OUTPUT_PATH}")
