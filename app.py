import streamlit as st
import pandas as pd
import sqlite3
import os

from langchain_groq import ChatGroq

# 🔐 Secure API key (DO NOT hardcode)
groq_api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="AI SQL Analyst", layout="wide")

st.title("🤖 AI SQL Data Analyst with Visualization")
st.write("Upload a CSV, ask questions, get SQL + charts!")

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
        api_key=groq_api_key,
        model="llama-3.1-8b-instant",
        temperature=0
    )

    # User query
    query = st.text_input("💬 Ask a question about your data")

    if query:
        with st.spinner("Generating SQL..."):

            prompt = f"""
            You are an expert SQL analyst.

            Table name: data_table

            Columns: {', '.join(df.columns)}

            Convert this question into SQL:
            "{query}"

            Only return plain SQL query. No markdown. No backticks.
            """

            sql_query = llm.invoke(prompt).content

            # Clean SQL
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

        st.subheader("🧾 Generated SQL")
        st.code(sql_query)

        try:
            result = pd.read_sql_query(sql_query, conn)

            st.subheader("✅ Result")
            st.dataframe(result)

            # 📊 Visualization
            if len(result.columns) >= 2:
                try:
                    import plotly.express as px

                    x_col = result.columns[0]
                    y_col = result.columns[1]

                    fig = px.bar(result, x=x_col, y=y_col, title="📊 Visualization")
                    st.plotly_chart(fig)

                except Exception:
                    st.warning("Could not generate visualization")

        except Exception as e:
            st.error(f"SQL Error: {e}")
