import pandas as pd


def format_value(value):
    if pd.isna(value):
        return "N/A"

    if isinstance(value, (int, float)):
        if abs(value) >= 1000000:
            return f"{value:,.2f}"
        if float(value).is_integer():
            return f"{int(value):,}"
        return f"{value:,.2f}"

    return str(value)


def get_first_numeric_column(df, exclude=None):
    exclude = set(exclude or [])
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    for col in numeric_cols:
        if col not in exclude:
            return col
    return None


def get_first_categorical_column(df, exclude=None):
    exclude = set(exclude or [])
    for col in df.columns:
        if col not in exclude and df[col].dtype == "object":
            return col
    return None


def generate_result_summary(df, plan):
    if df is None or df.empty:
        return "No rows were returned for this query."

    if len(df) == 1 and len(df.columns) == 1:
        value = df.iloc[0, 0]
        return f"The result is {format_value(value)}."

    if len(df) == 1:
        non_numeric_cols = [c for c in df.columns if df[c].dtype == "object"]
        numeric_col = get_first_numeric_column(df)

        if numeric_col:
            if non_numeric_cols:
                label = df.iloc[0][non_numeric_cols[0]]
                return f"For {label}, the value is {format_value(df.iloc[0][numeric_col])}."
            return f"The value is {format_value(df.iloc[0][numeric_col])}."

    if "year" in df.columns:
        numeric_col = get_first_numeric_column(df, exclude=["year"])
        if numeric_col and len(df) >= 2:
            sorted_df = df.sort_values("year")
            first_year = sorted_df.iloc[0]["year"]
            last_year = sorted_df.iloc[-1]["year"]
            first_val = sorted_df.iloc[0][numeric_col]
            last_val = sorted_df.iloc[-1][numeric_col]

            if last_val > first_val:
                direction = "increased"
            elif last_val < first_val:
                direction = "decreased"
            else:
                direction = "stayed flat"

            return (
                f"{numeric_col} {direction} from {format_value(first_val)} in {first_year} "
                f"to {format_value(last_val)} in {last_year}."
            )

    cat_col = get_first_categorical_column(df)
    numeric_col = get_first_numeric_column(df)

    if cat_col and numeric_col:
        top_row = df.sort_values(numeric_col, ascending=False).iloc[0]
        return (
            f"{top_row[cat_col]} has the highest {numeric_col} "
            f"at {format_value(top_row[numeric_col])}."
        )

    return f"The query returned {len(df)} rows."


def generate_result_highlights(df, plan, max_items=3):
    if df is None or df.empty:
        return []

    highlights = []
    cat_col = get_first_categorical_column(df)
    numeric_col = get_first_numeric_column(df)

    if cat_col and numeric_col and len(df) >= 2:
        sorted_df = df.sort_values(numeric_col, ascending=False)

        top_row = sorted_df.iloc[0]
        highlights.append(
            f"Top contributor: {top_row[cat_col]} ({format_value(top_row[numeric_col])})"
        )

        bottom_row = sorted_df.iloc[-1]
        highlights.append(
            f"Lowest contributor: {bottom_row[cat_col]} ({format_value(bottom_row[numeric_col])})"
        )

    if numeric_col:
        total = df[numeric_col].sum()
        highlights.append(f"Total {numeric_col}: {format_value(total)}")

    return highlights[:max_items]