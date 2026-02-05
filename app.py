import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# --------------------
# Page config
# --------------------
st.set_page_config(
    page_title="USA Housing Dashboard",
    layout="wide",
    page_icon="🏠",
    initial_sidebar_state="expanded"
)


# --------------------
# Load data
# --------------------
@st.cache_data
def load_data():
    df = pd.read_csv("USA Housing Dataset.csv")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df


df = load_data()


# --------------------
# Theme colors
# --------------------
TEXT_COLOR = "#F5F7FA"
CARD_BG = "rgba(0, 0, 0, 0.55)"
SIDEBAR_BG = "rgba(0, 0, 0, 0.75)"


# --------------------
# Background + UI CSS
# --------------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("https://images.unsplash.com/photo-1568605114967-8130f3a36994");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .block-container {{
        background-color: rgba(0,0,0,0.55);
        padding: 1.5rem;
        border-radius: 16px;
    }}

    [data-testid="stSidebar"] {{
        background-color: {SIDEBAR_BG};
    }}

    h1, h2, h3, h4, h5, h6, p, span, label {{
        color: {TEXT_COLOR};
    }}

    div[data-testid="metric-container"] {{
        background-color: {CARD_BG};
        border-radius: 14px;
        padding: 15px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }}

    .stDataFrame {{
        background-color: rgba(0,0,0,0.7);
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------
# Sidebar filters
# --------------------
st.sidebar.markdown(
    "<h2 style='color:white;'>🏠 Filters</h2>",
    unsafe_allow_html=True
)


price_min, price_max = int(df["price"].min()), int(df["price"].max())
price_range = st.sidebar.slider(
    "Price range",
    min_value=price_min,
    max_value=price_max,
    value=(price_min, price_max),
)

bedrooms_filter = st.sidebar.multiselect(
    "Bedrooms",
    sorted(df["bedrooms"].dropna().astype(int).unique()),
)

bathrooms_filter = st.sidebar.multiselect(
    "Bathrooms",
    sorted(df["bathrooms"].dropna().astype(int).unique()),
)

city_filter = st.sidebar.multiselect(
    "City",
    sorted(df["city"].dropna().unique())
)

state_filter = st.sidebar.multiselect(
    "State / Zip",
    sorted(df["statezip"].dropna().unique())
)


# --------------------
# SAFE Year filter (FIXED)
# --------------------
if "year" in df.columns:
    years = sorted(df["year"].dropna().unique())

    if len(years) > 1:
        year_range = st.sidebar.slider(
            "Year range",
            min_value=int(years[0]),
            max_value=int(years[-1]),
            value=(int(years[0]), int(years[-1])),
            step=1
        )
    else:
        year_range = (years[0], years[0])
        st.sidebar.info(f"📅 Data available only for year {years[0]}")
else:
    year_range = None


# --------------------
# Apply filters
# --------------------
filtered_df = df[
    (df["price"] >= price_range[0]) &
    (df["price"] <= price_range[1])
]

if bedrooms_filter:
    filtered_df = filtered_df[filtered_df["bedrooms"].isin(bedrooms_filter)]

if bathrooms_filter:
    filtered_df = filtered_df[filtered_df["bathrooms"].isin(bathrooms_filter)]

if city_filter:
    filtered_df = filtered_df[filtered_df["city"].isin(city_filter)]

if state_filter:
    filtered_df = filtered_df[filtered_df["statezip"].isin(state_filter)]

if year_range and "year" in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df["year"] >= year_range[0]) &
        (filtered_df["year"] <= year_range[1])
    ]


# --------------------
# Title
# --------------------
# st.title("🏙️ USA Housing Analytics Dashboard")
# st.caption("Beautiful scenic visualization of housing trends across the United States")

st.markdown(
    """
    <style>
    .hero-header {
        background-image: url(https://images.pexels.com/photos/258154/pexels-photo-258154.jpeg);
        background-size: cover;
        background-position: center;
        padding: 60px 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }

    .hero-title {
        font-size: 48px;
        font-weight: 800;
        color: white;
        text-shadow: 0 4px 20px rgba(0,0,0,0.9);
        margin-bottom: 10px;
    }

    .hero-subtitle {
        font-size: 18px;
        color: #F5F7FA;
        text-shadow: 0 2px 10px rgba(0,0,0,0.8);
    }
    </style>

    <div class="hero-header">
        <div class="hero-title">🏙️ USA Housing Analytics</div>
        <div class="hero-subtitle">
            Beautiful scenic visualization of housing trends across the United States
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown("---")


# --------------------
# KPIs
# --------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Average Price $",
    int(filtered_df["price"].mean()) if not filtered_df.empty else "N/A"
)

c2.metric("Median Area in Sqft", f"{filtered_df['sqft_living'].median():,.0f}")

c3.metric(
    "Avg Bedrooms",
    int(round(filtered_df["bedrooms"].mean())) if not filtered_df.empty else "N/A"
)


c4.metric(
    "Avg Bathrooms",
    int(round(filtered_df["bathrooms"].mean())) if not filtered_df.empty else "N/A"
)



st.markdown("---")


# --------------------
# Charts
# --------------------
st.subheader("📈 Price vs Living Area")

fig_scatter = px.scatter(
    filtered_df.sample(min(2000, len(filtered_df))),
    x="sqft_living",
    y="price",
    color="bedrooms",
    size="bathrooms",
    hover_data=["city", "statezip"]
)

# Update layout for medium dark background and white fonts/grids
fig_scatter.update_layout(
    plot_bgcolor="#424040",      # medium dark background inside plot
    paper_bgcolor="#2C2C2C",     # medium dark background around plot
    font_color="white",           # all text white
    xaxis=dict(
        showgrid=False,
        gridcolor="white",
        zeroline=False,
        title="Living Area (sqft)",
        tickfont=dict(color="white")
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="white",
        zeroline=False,
        title="Price ($)",
        tickfont=dict(color="white")
    ),
    legend=dict(
        title_font_color="white",
        font=dict(color="white")
    )
)

st.plotly_chart(fig_scatter, use_container_width=True)
# ------------------------------------------------------------

st.subheader("🛏️ Average Price by Bedrooms")

bed_price = filtered_df.groupby("bedrooms")["price"].mean().reset_index()

fig_bed = px.bar(
    bed_price,
    x="bedrooms",
    y="price",
    color="bedrooms",
)

# Update layout for medium dark background and white text/grid
fig_bed.update_layout(
    plot_bgcolor="#424040",      # medium dark inside plot
    paper_bgcolor="#2C2C2C",     # medium dark around plot
    font_color="white",           # all text white
    xaxis=dict(
        showgrid=False,
        gridcolor="white",
        zeroline=False,
        title="Bedrooms",
        tickfont=dict(color="white")
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="white",
        zeroline=False,
        title="Average Price ($)",
        tickfont=dict(color="white")
    ),
    showlegend=False               # optional: hide legend
)

st.plotly_chart(fig_bed, use_container_width=True)
# ------------------------------------------------------------

st.subheader("🗺️ Average Price by City (Top 20)")

city_price = (
    filtered_df.groupby("city")["price"]
    .mean()
    .reset_index()
    .sort_values("price", ascending=False)
    .head(20)
)

fig_city = px.bar(
    city_price,
    x="city",
    y="price",
    color="price",
    color_continuous_scale="Turbo"
)

# Same styling as Bedrooms chart
fig_city.update_layout(
    plot_bgcolor="#424040",      # medium dark plot background
    paper_bgcolor="#2C2C2C",     # medium dark outer background
    font_color="white",
    xaxis=dict(
        showgrid=False,
        gridcolor="white",
        zeroline=False,
        title="City",
        tickfont=dict(color="white")
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="white",
        zeroline=False,
        title="Average Price ($)",
        tickfont=dict(color="white")
    )
)

fig_city.update_xaxes(tickangle=45)

st.plotly_chart(fig_city, use_container_width=True)
# ------------------------------------------------------------

# --------------------
# Correlation
# --------------------
st.subheader("📊 Feature Correlation")

numeric_cols = filtered_df.select_dtypes(include=np.number)

if not numeric_cols.empty and len(numeric_cols.columns) > 1:
    corr = numeric_cols.corr().round(2)

    fig_corr = px.imshow(
        corr,
        text_auto=True,                 # show values like bars show labels
        color_continuous_scale="Turbo", # same vibrant feel as city bar chart
        zmin=-1,
        zmax=1,
        aspect="auto",
        template="plotly_dark"
    )

    fig_corr.update_layout(
        title=dict(
        text="📊 Correlation Between Numeric Features",
        font=dict(color="white", size=20)
    ),
        plot_bgcolor="#424040",      # medium dark plot background
        paper_bgcolor="#2C2C2C",     # medium dark outer background
        font_color="white",
        coloraxis_colorbar=dict(
            title="Correlation",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            tickfont=dict(color="white")
        )
    )

    fig_corr.update_xaxes(
        tickangle=45,
        side="bottom",
        tickfont=dict(color="white")
    )

    fig_corr.update_yaxes(
        autorange="reversed",
        tickfont=dict(color="white")
    )

    st.plotly_chart(fig_corr, use_container_width=True)

else:
    st.info("Not enough numeric data to compute correlation.")
# ------------------------------------------------------------

# --------------------
# Raw data
# --------------------
with st.expander("🔍 Show filtered raw data"):
    st.dataframe(filtered_df.head(200))

