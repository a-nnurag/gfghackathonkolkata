import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import google.generativeai as genai

from ui import load_ui
load_ui()
# Gemini API key
api_key="AIzaSyBGmfblE00s8i3AyPEy_O94fVe_55LOYSo"
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_sql(question):
    prompt = f"""
    Convert the following business question into SQL.

    Table name: claims

    Columns:
    life_insurer
    year
    claims_pending_start_no
    claims_pending_start_amt
    claims_intimated_no
    claims_intimated_amt
    total_claims_no
    total_claims_amt
    claims_paid_no
    claims_paid_amt
    claims_repudiated_no
    claims_repudiated_amt
    claims_rejected_no
    claims_rejected_amt
    claims_unclaimed_no
    claims_unclaimed_amt
    claims_pending_end_no
    claims_pending_end_amt
    claims_paid_ratio_no
    claims_paid_ratio_amt
    claims_repudiated_rejected_ratio_no
    claims_repudiated_rejected_ratio_amt
    claims_pending_ratio_no
    claims_pending_ratio_amt
    category

    Rules:
    - Return only SQL
    - No markdown
    - No explanation
    - Use table name claims
    - Use AS for aggregate aliases

    Question: {question}
    """
    response = model.generate_content(prompt)
    sql = response.text.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

def run_query(sql):
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

def choose_chart(df):
    cols = list(df.columns)

    if "year" in cols:
        return "line"
    elif len(cols) >= 2:
        return "bar"
    else:
        return "table"
    
def create_chart(df, chart):
    cols = list(df.columns)

    if chart == "line":
        if "year" in cols:
            x_col = "year"
            y_candidates = [c for c in cols if c != x_col and df[c].dtype != "object"]
            color_candidates = [c for c in cols if c != x_col and df[c].dtype == "object"]

            y_col = y_candidates[0] if y_candidates else None
            color_col = color_candidates[0] if color_candidates else None

            if y_col:
                if color_col:
                    fig = px.line(df, x=x_col, y=y_col, color=color_col, markers=True)
                else:
                    fig = px.line(df, x=x_col, y=y_col, markers=True)
                fig.update_traces(
                    line=dict(width=3),
                    marker=dict(size=8)
                )
            else:
                return None
        else:
            return None

    elif chart == "bar":
        cat_cols = [c for c in cols if df[c].dtype == "object"]
        num_cols = [c for c in cols if df[c].dtype != "object"]

        if len(cat_cols) >= 1 and len(num_cols) >= 1:
            x_col = cat_cols[0]
            y_col = num_cols[0]
            fig = px.bar(df, x=x_col, y=y_col)
        elif len(num_cols) >= 2:
            fig = px.bar(df, x=num_cols[0], y=num_cols[1])
        
            fig.update_traces(
            marker_line_width=0,
            opacity=0.92
            )
        else:
            return None

    else:
        return None

    fig.update_layout(
        dragmode="zoom",
        xaxis_title=cols[0],
        yaxis_title=cols[1] if len(cols) > 1 else "",
        height=500
    )


    return fig






# UI
st.markdown('<div class="main-title">AI Business Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask plain-English questions and get instant interactive business insights.</div>', unsafe_allow_html=True)


# question = st.text_input(
#     "Ask a business question"
# )

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
question = st.text_input("Ask a business question", placeholder="e.g. Show total claims paid amount by life insurer")
st.markdown('<div class="helper-text">Try: "Show claims paid ratio by insurer" or "Compare repudiated claims by year"</div>', unsafe_allow_html=True)
# generate = st.button("✨ Generate Dashboard")
st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚡ Dashboard Controls")
    st.markdown("Ask questions about insurance claims data.")
    st.markdown("---")
    st.markdown("### Suggested Prompts")
    st.markdown("- Show total claims paid amount by life insurer")
    st.markdown("- Show claims paid ratio by year")
    st.markdown("- Compare pending claims by insurer")
    st.markdown("- Show repudiated claims trend")



if st.button("✨ Generate Dashboard"):

    with st.spinner("Generating dashboard..."):

        sql = generate_sql(question)

        

        st.subheader("Generated SQL")
        st.code(sql)

        try:

            df = run_query(sql)

            numeric_cols = df.select_dtypes(include="number").columns.tolist()

            if len(df) > 0:
                k1, k2, k3 = st.columns(3)

                with k1:
                    st.markdown(f"""
                    <div class="metric-pill">
                        <div class="metric-label">Rows Returned</div>
                        <div class="metric-value">{len(df)}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with k2:
                    first_col = df.columns[0]
                    unique_count = df[first_col].nunique() if first_col in df.columns else 0
                    st.markdown(f"""
                    <div class="metric-pill">
                        <div class="metric-label">Unique {first_col}</div>
                        <div class="metric-value">{unique_count}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with k3:
                    if numeric_cols:
                        total_val = round(df[numeric_cols[0]].sum(), 2)
                        st.markdown(f"""
                        <div class="metric-pill">
                            <div class="metric-label">Total {numeric_cols[0]}</div>
                            <div class="metric-value">{total_val}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="metric-pill">
                            <div class="metric-label">Numeric Summary</div>
                            <div class="metric-value">N/A</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

            st.subheader("Data")
            st.dataframe(df)

            chart = choose_chart(df)

            fig = create_chart(df, chart)

            if fig is not None:
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "displaylogo": False,
                        "toImageButtonOptions": {
                            "format": "png",
                            "filename": "dashboard_chart",
                            "height": 600,
                            "width": 1000,
                            "scale": 2
                        }
                    }
                )
            else:
                st.warning("Could not create chart for this result.")



        except Exception as e:
            st.error(f"Query execution failed: {e}")