import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

# Set up the page configuration
st.set_page_config(layout="wide", page_title="Startup Funding Dashboard")

# Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv('https://github.com/anand738/Startup_Funding_Analysis/blob/master/startup_cleaned1.csv')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    return df

df = load_data()

# Helper functions
def format_cr(value, _):
    return f"{value:.0f} Cr"

def create_section_header(title):
    st.markdown(f"### {title}")

# Sidebar options
st.sidebar.title("Startup Funding Analysis")
option = st.sidebar.selectbox("Select View", ["Overall Analysis", "Startup", "Investor"])

# Overall Analysis
if option == "Overall Analysis":
    st.title("📊 Overall Startup Funding Analysis")

    # Summary Metrics
    total_funding = df['amount'].sum()
    max_funding = df['amount'].max()
    avg_funding = df.groupby('startup')['amount'].sum().mean()
    funded_startups = df['startup'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Funding", f"{total_funding:.0f} Cr")
    col2.metric("Highest Funding", f"{max_funding:.0f} Cr")
    col3.metric("Average Ticket Size", f"{avg_funding:.0f} Cr")
    col4.metric("Funded Startups", funded_startups)

    # Monthly Funding Analysis
    st.markdown("### 📈 Funding Trends (Month-on-Month)")
    selected_trend = st.selectbox("Select Trend", ["Total Funding", "Number of Investments"])
    trend_data = df.groupby(['year', 'month'])['amount'].agg(['sum', 'count']).reset_index()
    trend_data['month_year'] = trend_data['month'].astype(str) + "-" + trend_data['year'].astype(str)

    fig, ax = plt.subplots(figsize=(12, 6))
    if selected_trend == "Total Funding":
        sns.lineplot(x="month_year", y="sum", data=trend_data, ax=ax, marker="o")
        ax.set_ylabel("Total Funding (Cr)")
    else:
        sns.lineplot(x="month_year", y="count", data=trend_data, ax=ax, marker="o")
        ax.set_ylabel("Number of Investments")

    ax.set_xticks(ax.get_xticks()[::6])  # Show fewer x-axis labels
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Top Sectors
    st.markdown("### 🏆 Top Sectors")
    top_sectors = df.groupby('vertical').agg(total_funding=('amount', 'sum'), investments=('startup', 'count'))
    top_sectors = top_sectors.sort_values(by="total_funding", ascending=False).head(5)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(top_sectors.reset_index())
    with col2:
        fig, ax = plt.subplots()
        ax.pie(top_sectors['total_funding'], labels=top_sectors.index, autopct='%1.1f%%', startangle=140)
        ax.set_title("Funding Distribution by Sector")
        st.pyplot(fig)

# Startup Details
elif option == "Startup":
    st.sidebar.subheader("Select Startup")
    selected_startup = st.sidebar.selectbox("Choose a Startup", sorted(df['startup'].unique()))

    if selected_startup:
        st.title(f"🚀 {selected_startup} Details")

        # Key Metrics
        col1, col2, col3 = st.columns(3)
        location = df.loc[df['startup'] == selected_startup, 'city'].iloc[0]
        industry = df.loc[df['startup'] == selected_startup, 'vertical'].iloc[0]
        sub_vertical = df.loc[df['startup'] == selected_startup, 'subvertical'].iloc[0]

        col1.metric("Location", location)
        col2.metric("Industry", industry)
        col3.metric("Sub-vertical", sub_vertical)

        # Funding Rounds
        startup_data = df[df['startup'] == selected_startup]
        funding_data = startup_data[['date', 'round', 'amount', 'investors']].sort_values(by='date', ascending=False)

        st.markdown("### 💰 Funding Rounds")
        st.dataframe(funding_data.rename(columns={
            'date': 'Date',
            'round': 'Funding Round',
            'amount': 'Amount (Cr)',
            'investors': 'Investors'
        }))

# Investor Details
else:
    st.sidebar.subheader("Select Investor")
    all_investors = df['investors'].str.split(',').explode().str.strip().dropna().unique()
    selected_investor = st.sidebar.selectbox("Choose an Investor", sorted(all_investors))

    if selected_investor:
        st.title(f"💼 {selected_investor} Details")

        # Recent Investments
        investor_data = df[df['investors'].str.contains(selected_investor, na=False)]
        recent_investments = investor_data.sort_values(by='date', ascending=False).head(5)

        st.markdown("### 📅 Recent Investments")
        st.dataframe(recent_investments[['date', 'startup', 'vertical', 'amount']].rename(columns={
            'date': 'Date',
            'startup': 'Startup',
            'vertical': 'Sector',
            'amount': 'Amount (Cr)'
        }))

        # Biggest Investments
        st.markdown("### 🏆 Biggest Investments")
        top_investments = investor_data.groupby('startup')['amount'].sum().sort_values(ascending=False).head(5)

        fig, ax = plt.subplots()
        sns.barplot(x=top_investments.values, y=top_investments.index, palette="viridis", ax=ax)
        ax.set_xlabel("Total Funding (Cr)")
        st.pyplot(fig)

        # Investment Distribution by Sector
        st.markdown("### 📊 Sector-wise Investments")
        sector_data = investor_data.groupby('vertical')['amount'].sum().sort_values(ascending=False)

        fig, ax = plt.subplots()
        ax.pie(sector_data, labels=sector_data.index, autopct='%1.1f%%', startangle=140)
        ax.set_title("Investment Distribution by Sector")
        st.pyplot(fig)
