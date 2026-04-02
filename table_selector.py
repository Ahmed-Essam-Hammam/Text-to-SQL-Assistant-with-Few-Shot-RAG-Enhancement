from chains import table_selector_chain, safe_invoke
from database import list_all_tables


def get_relevant_tables(question, db_url: str = None, history=""):

    tables = list_all_tables(db_url=db_url)

    response = safe_invoke(
        table_selector_chain,
        {"question": question, "tables": tables, "history": history},
        fallback="__INJECTION__"
    )

    if response == "__INJECTION__":
        return "__INJECTION__"

    filtered = [
        t.strip() for t in response.split(",")
        if t.strip() in tables
    ]

    if not filtered:
        return tables

    return filtered
