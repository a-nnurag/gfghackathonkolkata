# import os

# import google.generativeai as genai
# import streamlit as st
# from streamlit.errors import StreamlitSecretNotFoundError

# from chart_utils import create_chart, create_frequency_chart, choose_chart, render_metrics
# from db_utils import TABLE_NAME, get_column_types, get_columns, run_query
# from followup import is_followup_question, refine_query_plan
# from metadata_handlers import (
#     classify_intent,
#     get_column_datatype,
#     get_dataset_overview,
#     get_null_count,
#     get_sample_values,
#     get_top_values,
#     get_unique_count,
# )
# from planner import build_sql_from_plan, generate_query_plan, summarize_plan
# from ui import load_ui

# load_ui()


# def load_api_key():
#     # api_key = os.getenv("API_KEY")
#     api_key="AIzaSyAw2_k0qnHySY6tO2GX1D3aCsRQJ3A6kpA"
#     if api_key:
#         return api_key

#     try:
#         return st.secrets["API_KEY"]
#     except (StreamlitSecretNotFoundError, KeyError):
#         return None


# def validate_sql(sql):
#     cleaned_sql = sql.strip().rstrip(";")
#     lowered_sql = cleaned_sql.lower()

#     if not lowered_sql.startswith("select"):
#         raise ValueError("Only SELECT queries are allowed.")

#     blocked_terms = [
#         "insert",
#         "update",
#         "delete",
#         "drop",
#         "alter",
#         "truncate",
#         "attach",
#         "pragma",
#     ]
#     if any(term in lowered_sql for term in blocked_terms):
#         raise ValueError("Unsafe SQL was generated and blocked.")

#     return cleaned_sql


# api_key = load_api_key()

# if api_key:
#     genai.configure(api_key=api_key)
#     model = genai.GenerativeModel("gemini-2.5-flash")
# else:
#     model = None


# if "last_plan" not in st.session_state:
#     st.session_state.last_plan = None

# if "last_question" not in st.session_state:
#     st.session_state.last_question = None

# if "last_sql" not in st.session_state:
#     st.session_state.last_sql = None


# st.markdown('<div class="main-title">AI Business Intelligence Dashboard</div>', unsafe_allow_html=True)
# st.markdown(
#     '<div class="subtitle">Ask plain-English questions and get instant interactive business insights.</div>',
#     unsafe_allow_html=True,
# )

# st.markdown('<div class="glass-card">', unsafe_allow_html=True)
# question = st.text_input(
#     "Ask a business question",
#     placeholder="e.g. Show total claims paid amount by life insurer",
# )
# st.markdown(
#     '<div class="helper-text">Try: "Show total claims paid amount by life insurer", then "Now only for 2023"</div>',
#     unsafe_allow_html=True,
# )
# st.markdown("</div>", unsafe_allow_html=True)

# with st.sidebar:
#     st.markdown("## ⚡ Dashboard Controls")
#     st.markdown("Ask questions about insurance claims data.")
#     st.markdown("---")
#     st.markdown("### Suggested Prompts")
#     st.markdown("- Show total claims paid amount by life insurer")
#     st.markdown("- Show claims paid ratio by year")
#     st.markdown("- Compare pending claims by insurer")
#     st.markdown("- What columns are in this dataset?")
#     st.markdown("- What is the datatype of claims_paid_amt?")
#     st.markdown("- Show top 10 values from life_insurer")
#     st.markdown("- Now only for 2023")
#     st.markdown("- Sort ascending")
#     st.markdown("- Top 5 only")

#     st.markdown("---")
#     st.markdown("### Follow-up Context")
#     if st.session_state.last_question:
#         st.caption(f"Last dashboard query: {st.session_state.last_question}")
#     else:
#         st.caption("No dashboard context yet.")

#     if st.button("Clear Follow-up Context"):
#         st.session_state.last_plan = None
#         st.session_state.last_question = None
#         st.session_state.last_sql = None
#         st.rerun()


# if st.button("✨ Generate Dashboard"):
#     if not question.strip():
#         st.warning("Please enter a question first.")
#     else:
#         with st.spinner("Generating dashboard..."):
#             try:
#                 columns = get_columns()
#                 intent = classify_intent(question, columns)

#                 if intent == "schema":
#                     row_count, schema_df = get_dataset_overview()
#                     st.subheader("Dataset Overview")
#                     st.info(f"This dataset has {row_count} rows and {len(schema_df)} columns.")
#                     st.dataframe(schema_df, use_container_width=True)

#                 elif intent == "sample_values":
#                     column_name, limit, sql, df = get_sample_values(question)
#                     st.subheader(f"Sample Values from {column_name}")
#                     st.code(sql)
#                     st.info(f"Showing up to {limit} distinct non-null values from `{column_name}`.")
#                     st.dataframe(df, use_container_width=True)

#                 elif intent == "column_type":
#                     column_name, dtype = get_column_datatype(question)
#                     st.subheader("Column Datatype")
#                     st.success(f"`{column_name}` has datatype: **{dtype}**")

#                 elif intent == "unique_count":
#                     column_name, sql, unique_count = get_unique_count(question)
#                     st.subheader("Unique Value Count")
#                     st.code(sql)
#                     st.success(f"`{column_name}` has **{unique_count}** unique values.")

#                 elif intent == "null_count":
#                     column_name, sql, null_count = get_null_count(question)
#                     st.subheader("Null Value Count")
#                     st.code(sql)
#                     st.success(f"`{column_name}` has **{null_count}** null values.")

#                 elif intent == "top_values":
#                     column_name, limit, sql, df = get_top_values(question)
#                     st.subheader(f"Top {limit} Values in {column_name}")
#                     st.code(sql)
#                     st.dataframe(df, use_container_width=True)

#                     fig = create_frequency_chart(df, column_name, "frequency")
#                     if fig is not None:
#                         st.plotly_chart(fig, use_container_width=True)

#                 else:
#                     column_types = get_column_types()

#                     if st.session_state.last_plan and is_followup_question(question):
#                         plan = refine_query_plan(
#                             question=question,
#                             previous_plan=st.session_state.last_plan,
#                             model=model,
#                             table_name=TABLE_NAME,
#                             column_types=column_types,
#                         )
#                         st.info(f"Applied as follow-up to: {st.session_state.last_question}")
#                     else:
#                         plan = generate_query_plan(
#                             question=question,
#                             model=model,
#                             table_name=TABLE_NAME,
#                             column_types=column_types,
#                         )

#                     sql = build_sql_from_plan(plan, TABLE_NAME)
#                     sql = validate_sql(sql)

#                     st.subheader("Query Plan")
#                     st.json(plan)
#                     st.caption(summarize_plan(plan))

#                     st.subheader("Generated SQL")
#                     st.code(sql)

#                     df = run_query(sql)

#                     st.session_state.last_plan = plan
#                     st.session_state.last_question = question
#                     st.session_state.last_sql = sql

#                     if df.empty:
#                         st.warning("The query ran successfully, but it returned no rows.")
#                     else:
#                         render_metrics(df)

#                         st.subheader(plan.get("title", "Data"))
#                         st.dataframe(df, use_container_width=True)

#                         chart = plan.get("chart_type") or choose_chart(df)
#                         fig = create_chart(df, chart)

#                         if fig is not None:
#                             st.plotly_chart(
#                                 fig,
#                                 use_container_width=True,
#                                 config={
#                                     "displaylogo": False,
#                                     "toImageButtonOptions": {
#                                         "format": "png",
#                                         "filename": "dashboard_chart",
#                                         "height": 600,
#                                         "width": 1000,
#                                         "scale": 2,
#                                     },
#                                 },
#                             )
#                         else:
#                             st.warning("Could not create chart for this result.")

#             except Exception as e:
#                 st.error(f"Request failed: {e}")

import os

import google.generativeai as genai
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from chart_utils import create_chart, create_frequency_chart, choose_chart, render_metrics
from dataset_manager import list_tables, preview_table, save_uploaded_csv
from db_utils import DEFAULT_TABLE, get_column_types, get_columns, get_row_count, run_query
from followup import is_followup_question, refine_query_plan
from metadata_handlers import (
    classify_intent,
    get_column_datatype,
    get_dataset_overview,
    get_null_count,
    get_sample_values,
    get_top_values,
    get_unique_count,
)
from planner import build_sql_from_plan, generate_query_plan, summarize_plan
from state_manager import (
    clear_followup_context,
    get_active_table,
    get_last_plan,
    get_last_question,
    init_session_state,
    set_active_table,
    set_last_plan,
    set_last_question,
    set_last_sql,
)
from ui import load_ui

load_ui()
init_session_state()

from error_handlers import format_user_error
from insight_generator import generate_result_highlights, generate_result_summary
from schema_utils import get_schema_profile


def load_api_key():
    api_key = os.getenv("API_KEY")
    api_key="AIzaSyAR6_2DNwHP0X1brpz8-RKottIXyUDWK28"
    if api_key:
        return api_key

    try:
        return st.secrets["API_KEY"]
    except (StreamlitSecretNotFoundError, KeyError):
        return None


def validate_sql(sql):
    cleaned_sql = sql.strip().rstrip(";")
    lowered_sql = cleaned_sql.lower()

    if not lowered_sql.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    blocked_terms = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "attach",
        "pragma",
    ]
    if any(term in lowered_sql for term in blocked_terms):
        raise ValueError("Unsafe SQL was generated and blocked.")

    return cleaned_sql


api_key = load_api_key()

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    model = None


st.markdown('<div class="main-title">AI Business Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Ask plain-English questions and get instant interactive business insights.</div>',
    unsafe_allow_html=True,
)

# Sidebar: dataset management
with st.sidebar:
    st.markdown("## 📁 Dataset Manager")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        if st.button("Load Uploaded CSV"):
            try:
                table_name, df_uploaded = save_uploaded_csv(uploaded_file)
                set_active_table(table_name)
                clear_followup_context()
                st.success(f"Loaded dataset as table: `{table_name}`")
                st.dataframe(df_uploaded.head(5), use_container_width=True)
                st.rerun()
            except Exception as e:
                st.error(f"Upload failed: {e}")

    available_tables = list_tables()
    if DEFAULT_TABLE not in available_tables:
        available_tables = [DEFAULT_TABLE] + available_tables

    current_active = get_active_table()
    if current_active not in available_tables:
        current_active = DEFAULT_TABLE
        set_active_table(current_active)

    selected_table = st.selectbox(
        "Select active dataset",
        options=available_tables,
        index=available_tables.index(current_active),
    )

    if selected_table != current_active:
        set_active_table(selected_table)
        clear_followup_context()
        st.rerun()

    active_table = get_active_table()

    st.markdown("---")
    st.markdown("### Active Dataset")
    st.caption(f"Table: `{active_table}`")

    try:
        row_count = get_row_count(active_table)
        columns = get_columns(active_table)
        st.caption(f"Rows: {row_count}")
        st.caption(f"Columns: {len(columns)}")
    except Exception:
        st.caption("Could not load dataset metadata.")

    if st.button("Preview Active Dataset"):
        try:
            preview_df = preview_table(active_table, limit=10)
            st.dataframe(preview_df, use_container_width=True)
        except Exception as e:
            st.error(f"Preview failed: {e}")

    st.markdown("---")
    st.markdown("### Suggested Prompts")
    st.markdown("- What columns are in this dataset?")
    st.markdown("- What is the datatype of claims_paid_amt?")
    st.markdown("- Show top 10 values from life_insurer")
    st.markdown("- Show total claims paid amount by life insurer")
    st.markdown("- Now only for 2023")
    st.markdown("- Top 5 only")

    st.markdown("---")
    st.markdown("### Follow-up Context")
    if get_last_question():
        st.caption(f"Last dashboard query: {get_last_question()}")
    else:
        st.caption("No dashboard context yet.")

    if st.button("Clear Follow-up Context"):
        clear_followup_context()
        st.rerun()

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
question = st.text_input(
    "Ask a business question",
    placeholder="e.g. Show total claims paid amount by life insurer",
)
st.markdown(
    f'<div class="helper-text">Current dataset: <b>{get_active_table()}</b>. Try: "Show total claims paid amount by life insurer", then "Now only for 2023"</div>',
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)


if st.button("✨ Generate Dashboard"):
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Generating dashboard..."):
            try:
                active_table = get_active_table()
                columns = get_columns(active_table)
                intent = classify_intent(question, columns)

                if intent == "schema":
                    row_count, schema_df = get_dataset_overview(active_table)
                    st.subheader("Dataset Overview")
                    st.info(
                        f"Active dataset `{active_table}` has {row_count} rows and {len(schema_df)} columns."
                    )
                    st.dataframe(schema_df, use_container_width=True)

                elif intent == "sample_values":
                    column_name, limit, sql, df = get_sample_values(question, active_table)
                    st.subheader(f"Sample Values from {column_name}")
                    st.code(sql)
                    st.info(f"Showing up to {limit} distinct non-null values from `{column_name}`.")
                    st.dataframe(df, use_container_width=True)

                elif intent == "column_type":
                    column_name, dtype = get_column_datatype(question, active_table)
                    st.subheader("Column Datatype")
                    st.success(f"`{column_name}` has datatype: **{dtype}**")

                elif intent == "unique_count":
                    column_name, sql, unique_count = get_unique_count(question, active_table)
                    st.subheader("Unique Value Count")
                    st.code(sql)
                    st.success(f"`{column_name}` has **{unique_count}** unique values.")

                elif intent == "null_count":
                    column_name, sql, null_count = get_null_count(question, active_table)
                    st.subheader("Null Value Count")
                    st.code(sql)
                    st.success(f"`{column_name}` has **{null_count}** null values.")

                elif intent == "top_values":
                    column_name, limit, sql, df = get_top_values(question, active_table)
                    st.subheader(f"Top {limit} Values in {column_name}")
                    st.code(sql)
                    st.dataframe(df, use_container_width=True)

                    summary = generate_result_summary(df, {"chart_type": "bar"})
                    if summary:
                        st.success(summary)

                    fig = create_frequency_chart(df, column_name, "frequency")
                    if fig is not None:
                        st.plotly_chart(fig, use_container_width=True)

                else:
                    schema_profile = get_schema_profile(active_table)
                    column_types = {col["name"]: col["type"] for col in schema_profile["columns"]}

                    last_plan = get_last_plan()
                    if last_plan and is_followup_question(question):
                        plan = refine_query_plan(
                            question=question,
                            previous_plan=last_plan,
                            model=model,
                            table_name=active_table,
                            column_types=column_types,
                            schema_profile=schema_profile,
                        )
                        st.info(f"Applied as follow-up to: {get_last_question()}")
                    else:
                        plan = generate_query_plan(
                            question=question,
                            model=model,
                            table_name=active_table,
                            column_types=column_types,
                            schema_profile=schema_profile,
                        )

                    sql = build_sql_from_plan(plan, active_table)
                    sql = validate_sql(sql)

                    st.subheader("Query Plan")
                    st.json(plan)
                    st.caption(summarize_plan(plan))

                    st.subheader("Generated SQL")
                    st.code(sql)

                    df = run_query(sql)

                    set_last_plan(plan)
                    set_last_question(question)
                    set_last_sql(sql)

                    if df.empty:
                        st.warning("The query ran successfully, but it returned no rows.")
                    else:
                        render_metrics(df)

                        st.subheader(plan.get("title", "Data"))
                        st.dataframe(df, use_container_width=True)

                        summary = generate_result_summary(df, plan)
                        if summary:
                            st.success(summary)

                        highlights = generate_result_highlights(df, plan)
                        for item in highlights:
                            st.markdown(f"- {item}")

                        chart = plan.get("chart_type") or choose_chart(df)
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
                                        "scale": 2,
                                    },
                                },
                            )
                        else:
                            st.warning("Could not create chart for this result.")

            except Exception as e:
                active_table_name = get_active_table()
                available_columns = []
                try:
                    available_columns = get_columns(active_table_name)
                except Exception:
                    pass

                st.error(
                    format_user_error(
                        error=e,
                        active_table=active_table_name,
                        columns=available_columns,
                    )
                )