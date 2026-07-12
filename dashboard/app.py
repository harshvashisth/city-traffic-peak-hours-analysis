import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="City Traffic Peak Hours Analysis",
    page_icon="🚦",
    layout="wide"
)

sns.set_style("whitegrid")

# -------------------------------------------------
# Title
# -------------------------------------------------
st.title("🚦 City Traffic Peak Hours Analysis")
st.markdown(
    "Interactive dashboard analyzing **Uber NYC pickup data** to identify "
    "peak hours, weekday patterns, and demand hotspots."
)

# -------------------------------------------------
# Load Data
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/uber-raw-data-apr14.csv")
    df["Date/Time"] = pd.to_datetime(df["Date/Time"], format="%m/%d/%Y %H:%M:%S")
    df["Hour"] = df["Date/Time"].dt.hour
    df["Weekday"] = df["Date/Time"].dt.day_name()
    df["Day"] = df["Date/Time"].dt.day
    df.drop_duplicates(inplace=True)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "Dataset not found. Please download `uber-raw-data-apr14.csv` from Kaggle "
        "(fivethirtyeight/uber-pickups-in-new-york-city) and place it inside the `data/` folder."
    )
    st.stop()

weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# -------------------------------------------------
# Sidebar Filters
# -------------------------------------------------
st.sidebar.header("🔎 Filters")

selected_days = st.sidebar.multiselect(
    "Select Day(s) of Week",
    options=weekday_order,
    default=weekday_order
)

hour_range = st.sidebar.slider(
    "Select Hour Range",
    min_value=0, max_value=23, value=(0, 23)
)

filtered_df = df[
    (df["Weekday"].isin(selected_days)) &
    (df["Hour"] >= hour_range[0]) &
    (df["Hour"] <= hour_range[1])
]

# -------------------------------------------------
# KPI Cards
# -------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Trips (filtered)", f"{len(filtered_df):,}")

with col2:
    if not filtered_df.empty:
        peak_hour = filtered_df.groupby("Hour").size().idxmax()
        st.metric("Peak Hour", f"{peak_hour}:00")
    else:
        st.metric("Peak Hour", "N/A")

with col3:
    if not filtered_df.empty:
        busiest_day = filtered_df.groupby("Weekday").size().idxmax()
        st.metric("Busiest Day", busiest_day)
    else:
        st.metric("Busiest Day", "N/A")

st.divider()

# -------------------------------------------------
# Hourly Pickup Chart
# -------------------------------------------------
st.subheader("📊 Pickups by Hour of Day")

hourly_counts = filtered_df.groupby("Hour").size().reindex(range(24), fill_value=0)

fig1, ax1 = plt.subplots(figsize=(12, 5))
sns.barplot(x=hourly_counts.index, y=hourly_counts.values, palette="viridis", ax=ax1)
ax1.set_xlabel("Hour of Day")
ax1.set_ylabel("Number of Pickups")
st.pyplot(fig1)

# -------------------------------------------------
# Heatmap
# -------------------------------------------------
st.subheader("🔥 Hour vs Weekday Heatmap")

pivot = filtered_df.pivot_table(
    index="Weekday", columns="Hour", values="Date/Time", aggfunc="count"
).reindex([d for d in weekday_order if d in selected_days])

fig2, ax2 = plt.subplots(figsize=(14, 5))
sns.heatmap(pivot, cmap="YlOrRd", linewidths=0.3, ax=ax2)
st.pyplot(fig2)

# -------------------------------------------------
# Geographic Density
# -------------------------------------------------
st.subheader("🗺️ Pickup Location Density")

fig3, ax3 = plt.subplots(figsize=(8, 8))
ax3.scatter(filtered_df["Lon"], filtered_df["Lat"], s=0.5, alpha=0.2, color="steelblue")
ax3.set_xlabel("Longitude")
ax3.set_ylabel("Latitude")
st.pyplot(fig3)

# -------------------------------------------------
# Raw Data Preview
# -------------------------------------------------
with st.expander("📄 View Filtered Raw Data"):
    st.dataframe(filtered_df.head(100))

st.markdown("---")
st.caption("Built with Streamlit | Data: Uber NYC Pickups (fivethirtyeight, Kaggle)")
