# -*- coding: utf-8 -*-
"""Store throughput .ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/174GtBSnRqdHFgddBTGoStEbtyGYkC2Wh
"""

pip install pandas openpyxl numpy gspread gspread_dataframe oauth2client

!pip install streamlit pandas openpyxl numpy

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Function to compute all metrics
def calculate_metrics(df):
    df['TY'] = df[['April', 'May', 'June']].sum(axis=1)
    df['Avg_Monthly_Sales'] = df['TY'] / 3
    df['Throughput_%'] = round(df['TY'] / (df['TY'] + df['SOH']) * 100, 2)
    df['YoY_Growth_%'] = round((df['TY'] - df['LY']) / df['LY'] * 100, 2)
    df['MoM_Growth_%'] = round((df['June'] - df['April']) / df['April'] * 100, 2)
    df['Stock_Coverage_Months'] = round(df['SOH'] / df['Avg_Monthly_Sales'], 2)

    df['Efficiency_Score'] = (
        0.4 * (df['Throughput_%'] / 100) +
        0.3 * (df['YoY_Growth_%'] / 100) +
        0.2 * (df['MoM_Growth_%'] / 100) +
        0.1 * (1 / (df['Stock_Coverage_Months'].replace(0, np.nan))).fillna(0)
    )

    df['Store_Rank'] = df['Efficiency_Score'].rank(ascending=False).astype(int)
    return df

# Category level summary
def generate_category_summary(df):
    summary = df.groupby('Category').agg({
        'TY': 'sum',
        'LY': 'sum',
        'Throughput_%': 'mean',
        'YoY_Growth_%': 'mean',
        'Stock_Coverage_Months': 'mean'
    }).reset_index()
    summary['YoY_Growth_Total_%'] = round((summary['TY'] - summary['LY']) / summary['LY'] * 100, 2)
    return summary

# Export to Excel
def to_excel(store_df, summary_df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        store_df.to_excel(writer, index=False, sheet_name='Store Metrics')
        summary_df.to_excel(writer, index=False, sheet_name='Category Summary')
    output.seek(0)
    return output

# Streamlit App UI
st.set_page_config(page_title="Store Inventory Dashboard", layout="wide")
st.title("📦 Store Inventory Management Dashboard")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)

        required_cols = {'Item Code', 'Store Code', 'Category', 'April', 'May', 'June', 'LY', 'SOH'}
        if not required_cols.issubset(df.columns):
            st.error(f"❌ Missing required columns. Required: {required_cols}")
        else:
            st.success("✅ File uploaded successfully.")
            with st.spinner("Analyzing data..."):
                df_metrics = calculate_metrics(df)
                df_summary = generate_category_summary(df_metrics)

                st.subheader("🏬 Store Level Metrics")
                st.dataframe(df_metrics.style.format({'Throughput_%': '{:.2f}', 'YoY_Growth_%': '{:.2f}', 'MoM_Growth_%': '{:.2f}', 'Stock_Coverage_Months': '{:.2f}', 'Efficiency_Score': '{:.3f}'}))

                st.subheader("📊 Category Summary")
                st.dataframe(df_summary)

                excel_data = to_excel(df_metrics, df_summary)
                st.download_button("📥 Download Excel Report", data=excel_data, file_name="Store_Inventory_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("📄 Please upload an Excel file with required columns to begin.")