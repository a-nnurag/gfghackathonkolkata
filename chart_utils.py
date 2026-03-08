import plotly.express as px
import streamlit as st


def choose_chart(df):
    cols = list(df.columns)
    num_cols = [c for c in cols if df[c].dtype != "object"]

    if "year" in cols and len(num_cols) >= 1:
        return "line"
    if len(cols) >= 2:
        return "bar"
    return "table"


def create_chart(df, chart):
    cols = list(df.columns)

    if chart == "line":
        if "year" not in cols:
            return None

        x_col = "year"
        y_candidates = [c for c in cols if c != x_col and df[c].dtype != "object"]
        color_candidates = [c for c in cols if c != x_col and df[c].dtype == "object"]

        y_col = y_candidates[0] if y_candidates else None
        color_col = color_candidates[0] if color_candidates else None

        if not y_col:
            return None

        if color_col:
            fig = px.line(df, x=x_col, y=y_col, color=color_col, markers=True)
        else:
            fig = px.line(df, x=x_col, y=y_col, markers=True)

        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        fig.update_layout(height=500)
        return fig

    if chart == "bar":
        cat_cols = [c for c in cols if df[c].dtype == "object"]
        num_cols = [c for c in cols if df[c].dtype != "object"]

        if len(cat_cols) >= 1 and len(num_cols) >= 1:
            fig = px.bar(df, x=cat_cols[0], y=num_cols[0])
        elif len(num_cols) >= 2:
            fig = px.bar(df, x=num_cols[0], y=num_cols[1])
            fig.update_traces(marker_line_width=0, opacity=0.92)
        else:
            return None

        fig.update_layout(height=500)
        return fig

    if chart == "pie":
        if len(cols) >= 2:
            fig = px.pie(df, names=cols[0], values=cols[1])
            fig.update_layout(height=500)
            return fig
        return None

    return None


def create_frequency_chart(df, x_col, y_col="frequency"):
    if x_col not in df.columns or y_col not in df.columns:
        return None
    fig = px.bar(df, x=x_col, y=y_col)
    fig.update_layout(height=500)
    return fig


def render_metrics(df):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if len(df) == 0:
        return

    k1, k2, k3 = st.columns(3)

    with k1:
        st.markdown(
            f"""
            <div class="metric-pill">
                <div class="metric-label">Rows Returned</div>
                <div class="metric-value">{len(df)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k2:
        first_col = df.columns[0]
        unique_count = df[first_col].nunique() if first_col in df.columns else 0
        st.markdown(
            f"""
            <div class="metric-pill">
                <div class="metric-label">Unique {first_col}</div>
                <div class="metric-value">{unique_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k3:
        if numeric_cols:
            total_val = round(df[numeric_cols[0]].sum(), 2)
            label = f"Total {numeric_cols[0]}"
            value = total_val
        else:
            label = "Numeric Summary"
            value = "N/A"

        st.markdown(
            f"""
            <div class="metric-pill">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)