import streamlit as st
import pandas as pd
import sqlite3
import os

from langchain_groq import ChatGroq

# 🔑 ADD YOUR GROQ API KEY
os.environ["GROQ_API_KEY"] = "your_api_key"

st.set_page_config(page_title="AI SQL Analyst", layout="wide")

st.title("🤖 AI SQL Data Analyst (Stable Version)")
st.write("Upload a CSV and ask questions in plain English!")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Data Preview")
    st.dataframe(df.head())

    # Convert CSV → SQLite
    conn = sqlite3.connect("data.db")
    df.to_sql("data_table", conn, if_exists="replace", index=False)

    # Setup LLM
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0
    )

    # User query
    query = st.text_input("💬 Ask a question about your data")

    if query:
        with st.spinner("Generating SQL..."):

            # Step 1: Ask AI to generate SQL
            prompt = f"""
            You are an expert SQL analyst.

            Table name: data_table

            Columns: {', '.join(df.columns)}

            Convert this question into SQL:
            "{query}"

            Only return SQL query. No explanation.
            """

            sql_query = llm.invoke(prompt).content

        st.subheader("🧾 Generated SQL")
        st.code(sql_query)

        # Step 2: Execute SQL
        try:
            result = pd.read_sql_query(sql_query, conn)

            st.subheader("✅ Result")
            st.dataframe(result)

        except Exception as e:
            st.error(f"SQL Error: {e}")