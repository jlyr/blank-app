import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import csv
import io

st.title("LOL Dataset Key Visualizations")
st.write("This app displays key visualizations based on the LOL dataset using the same code used in the original notebook.")

# ----------------------------
# Data Loading & Preprocessing
# ----------------------------
def load_data():
    try:
        # on_bad_lines='skip' handles rows with extra or missing fields.
        df = pd.read_csv("Data PM - case (1).csv",
                         on_bad_lines='skip',
                         engine='python',
                         quoting=csv.QUOTE_MINIMAL)
        return df
    except FileNotFoundError:
        st.error("CSV file not found.")
        return None
    except pd.errors.ParserError as e:
        st.error(f"ParserError: {e}")
        return None

# Function to parse the JSON column and extract total_balance
def parse_json_column(value):
    try:
        json_data = json.loads(value)
        return json_data.get("total_balance")
    except (json.JSONDecodeError, TypeError, AttributeError):
        return None

# Load Data
df = load_data()

if df is not None:
    # ----------------------------
    # Data Preview and Summary (from the original file)
    # ----------------------------
    st.subheader("Data Preview")
    st.dataframe(df.head())
    st.write("**Shape of the DataFrame:**", df.shape)
    
    st.subheader("DataFrame Info")
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    st.text(info_str)
    
    st.subheader("Descriptive Statistics (Numerical Columns)")
    st.write(df.describe())
    
    # Unique values and frequency for categorical column "CURRENCY_CODE" (if available)
    if 'CURRENCY_CODE' in df.columns:
        st.subheader("Unique Values and Frequency in 'CURRENCY_CODE'")
        st.write("Unique values:", df['CURRENCY_CODE'].unique())
        st.write("Value counts:")
        st.write(df['CURRENCY_CODE'].value_counts())
    else:
        st.warning("Column 'CURRENCY_CODE' not found.")
    
    # ----------------------------
    # Parse JSON column to extract total_balance (as in the original file)
    # ----------------------------
    if 'POST_TRANSACTION_ACCOUNT_BALANCES' in df.columns:
        st.subheader("Parsing 'POST_TRANSACTION_ACCOUNT_BALANCES' to Extract total_balance")
        df['total_balance'] = df['POST_TRANSACTION_ACCOUNT_BALANCES'].apply(parse_json_column)
        st.dataframe(df[['POST_TRANSACTION_ACCOUNT_BALANCES', 'total_balance']].head())
    else:
        st.warning("Column 'POST_TRANSACTION_ACCOUNT_BALANCES' not found.")
    
    # ----------------------------
    # Visualization 1: Distribution of Transaction Amounts
    # ----------------------------
    st.subheader("1. Distribution of Transaction Amounts")
    if 'TRANSACTION_AMOUNT' in df.columns:
        fig1, ax1 = plt.subplots()
        sns.histplot(df['TRANSACTION_AMOUNT'].dropna(), bins=30, kde=True, ax=ax1)
        ax1.set_title("Distribution of Transaction Amounts")
        ax1.set_xlabel("Transaction Amount")
        st.pyplot(fig1)
    else:
        st.warning("Column 'TRANSACTION_AMOUNT' not found. Cannot display Distribution of Transaction Amounts.")
    
    # ----------------------------
    # Visualization 2: Box Plot of Transaction Amounts by Currency
    # ----------------------------
    st.subheader("2. Box Plot of Transaction Amounts by Currency")
    if 'TRANSACTION_AMOUNT' in df.columns and 'CURRENCY_CODE' in df.columns:
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.boxplot(x='CURRENCY_CODE', y='TRANSACTION_AMOUNT', data=df, ax=ax2)
        ax2.set_title("Transaction Amounts by Currency")
        ax2.set_xlabel("Currency Code")
        ax2.set_ylabel("Transaction Amount")
        st.pyplot(fig2)
    else:
        st.warning("Columns 'TRANSACTION_AMOUNT' and/or 'CURRENCY_CODE' not found. Cannot display Box Plot of Transaction Amounts by Currency.")
    
    # ----------------------------
    # Visualization 3: Top 10 Merchant Category Codes (MCC)
    # ----------------------------
    st.subheader("3. Top 10 Merchant Category Codes (MCC)")
    if 'MCC' in df.columns:
        top_mcc = df['MCC'].value_counts().head(10)
        fig3, ax3 = plt.subplots()
        sns.barplot(x=top_mcc.values, y=top_mcc.index, ax=ax3, palette='viridis')
        ax3.set_title("Top 10 Merchant Category Codes")
        ax3.set_xlabel("Frequency")
        ax3.set_ylabel("MCC")
        st.pyplot(fig3)
    else:
        st.warning("Column 'MCC' not found. Cannot display Top 10 MCC visualization.")
    
    # ----------------------------
    # Visualization 4: Scatter Plot of Transaction Amount vs. Total Balance
    # ----------------------------
    st.subheader("4. Scatter Plot: Transaction Amount vs. Total Balance")
    if 'TRANSACTION_AMOUNT' in df.columns and 'total_balance' in df.columns:
        fig4, ax4 = plt.subplots()
        sns.scatterplot(x='TRANSACTION_AMOUNT', y='total_balance', data=df, ax=ax4)
        ax4.set_title("Transaction Amount vs. Total Balance")
        ax4.set_xlabel("Transaction Amount")
        ax4.set_ylabel("Total Balance")
        st.pyplot(fig4)
    else:
        st.warning("Columns 'TRANSACTION_AMOUNT' and/or 'total_balance' not found. Cannot display Scatter Plot.")
    
    # ----------------------------
    # Visualization 5: Time Series of Transaction Amounts (if Timestamp data available)
    # ----------------------------
    st.subheader("5. Time Series of Transaction Amounts")
    if 'TRANSACTION_AMOUNT' in df.columns and 'TIMESTAMP' in df.columns:
        try:
            df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
            df.sort_values('TIMESTAMP', inplace=True)
            # Resample transaction amounts over a daily frequency (or adjust as needed)
            ts_df = df[['TIMESTAMP', 'TRANSACTION_AMOUNT']].dropna()
            ts_df = ts_df.set_index('TIMESTAMP').resample('D').sum()
            st.line_chart(ts_df)
        except Exception as e:
            st.error(f"Error processing TIMESTAMP column: {e}")
    else:
        st.warning("Columns 'TRANSACTION_AMOUNT' and/or 'TIMESTAMP' not found. Cannot display Time Series of Transaction Amounts.")
else:
    st.error("No data loaded. Please ensure the CSV file exists and is formatted correctly.")
