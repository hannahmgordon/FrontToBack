import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load dataset once
@st.cache_data

def load_data():
    data = pd.read_csv("final_cleaned_output.csv")
    data["Filing Date"] = pd.to_datetime(data["Filing Date"])
    data["Return Date"] = pd.to_datetime(data["Return Date"])
    data["YearMonth"] = data["Return Date"].dt.to_period("M").dt.to_timestamp()
    return data

data = load_data()

# Load S&P 500 benchmark data
sp500 = pd.read_csv("SP500_historical.csv")
sp500["date"] = pd.to_datetime(sp500["date"])
sp500["Year"] = sp500["date"].dt.year
sp500.columns = sp500.columns.str.strip()
sp500 = sp500.rename(columns={"Return": "SP500_Return"})

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Annual 10-K Returns by Company", "Cosine Similarity vs Monthly Return Over Time", "Report"])

# ---------- Page: Home ----------
if page == "Home":
    st.title("Home")
    st.write("Welcome to the 10-K Analysis Dashboard.")

# ---------- Page: Annual 10-K Returns by Company ----------
elif page == "Annual 10-K Returns by Company":
    st.title("Annual 10-K Returns by Company")

    st.sidebar.header("Select a Company")
    all_symbols = sorted(data["Symbol"].unique())
    selected_symbol = st.sidebar.selectbox("Choose a company:", all_symbols)

    bin_colors = {
        1: "#ff0000",
        2: "#ffa700",
        3: "#fff400",
        4: "#a3ff00",
        5: "#2cba00"
    }

    bin_labels = {
        1: "Bin 1 (largest change in 10-K)",
        2: "Bin 2",
        3: "Bin 3",
        4: "Bin 4",
        5: "Bin 5 (smallest change in 10-K)"
    }

    if selected_symbol:
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot S&P 500 returns as faint line
        sp500_filtered = sp500[sp500["Year"] >= 2004]
        ax.plot(sp500_filtered["Year"], sp500_filtered["SP500_Return"], color="#bbbbbb", linewidth=2, alpha=0.6)

        # Plot selected company with bin coloring
        symbol_df = data[data["Symbol"] == selected_symbol]
        yearly = symbol_df.groupby("Year").agg({"Return": "mean", "Bins": "first"}).reset_index()
        yearly = yearly.sort_values("Year")

        for i in range(len(yearly) - 1):
            x_vals = [yearly["Year"].iloc[i], yearly["Year"].iloc[i+1]]
            y_vals = [yearly["Return"].iloc[i], yearly["Return"].iloc[i+1]]
            bin_val = yearly["Bins"].iloc[i]
            color = bin_colors.get(bin_val, "#000000")
            ax.plot(x_vals, y_vals, color=color, linewidth=3)

        ax.set_title("Yearly Returns Around 10-K Filing", fontsize=16)
        ax.set_xlabel("Year", fontsize=12)
        ax.set_ylabel("Return", fontsize=12)

        # Clean grid with light grey and selected ticks
        ax.grid(which='major', axis='y', color='#dddddd', linewidth=1, linestyle='-', alpha=0.5)
        ax.axhline(y=0, color='#dddddd', linewidth=1, linestyle='-', alpha=0.5)

        # Set vertical ticks every 5 years only
        all_years = sorted(set(yearly["Year"]).union(sp500_filtered["Year"] if not sp500_filtered.empty else []))
        ax.set_xticks(all_years)
        ax.set_xticklabels([str(y) if y % 2 == 0 else '' for y in all_years])

        # Add major gridlines every 5 years only
        for y in all_years:
            if y % 5 == 0:
                ax.axvline(x=y, color='#dddddd', linewidth=1, linestyle='-', alpha=0.5)
                pass  # fixed erroneous list comprehension

        st.pyplot(fig)

        st.markdown("### Bin Color Legend")
        bin_legend = "&emsp;".join(
            [f"<span style='color:{bin_colors[b]}; font-weight:bold;'>■</span> {bin_labels[b]}" for b in sorted(bin_colors)]
        )
        sp500_note = "<span style='color:#bbbbbb; font-weight:bold;'>■</span> S&P 500 Annual Return (faint grey line)"
        st.markdown(f"<div style='font-size:16px;'>{bin_legend}&emsp;{sp500_note}</div>", unsafe_allow_html=True)
    else:
        st.info("Please select a company to view the chart.")

# ---------- Page: Cosine Similarity vs Monthly Return Over Time ----------
elif page == "Cosine Similarity vs Monthly Return Over Time":
    st.title("Cosine Similarity vs Monthly Return Over Time")

    symbols = sorted(data["Symbol"].unique())
    selected_symbol = st.sidebar.selectbox("Choose a company:", symbols)

    firm_df = data[data["Symbol"] == selected_symbol].copy()

    filing_series = firm_df.groupby("Filing Date")["Cosine Similarity"].first().sort_index()
    monthly_return = firm_df.groupby("YearMonth")["Return"].mean().rolling(3, min_periods=1).mean()

    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(filing_series.index, filing_series.values, 'o-', color="blue", label="Cosine Similarity")
    ax1.set_ylabel("Cosine Similarity", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")

    ax2 = ax1.twinx()
    ax2.plot(monthly_return.index, monthly_return.values, '-s', color="darkorange", label="Return (smoothed)")
    ax2.set_ylabel("Return (%)", color="darkorange")
    ax2.tick_params(axis="y", labelcolor="darkorange")

    plt.title(f"{selected_symbol} - Cosine Similarity & Returns Over Time")
    fig.tight_layout()

    st.pyplot(fig)
    st.markdown("**Note:** Cosine Similarity is based on filing date (blue), returns are monthly with 3-month smoothing (orange).")

# ---------- Page: Report ----------
else:
    st.title("Report")
    st.write("Coming soon.")
