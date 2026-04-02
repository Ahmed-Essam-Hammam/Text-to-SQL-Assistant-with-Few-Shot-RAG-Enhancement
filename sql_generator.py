from chains import sql_chain, sql_fix_chain, fallback_chain
from sql_validator import validate_sql
from rag.retriever import retrieve_examples


def get_sql(question, schema, examples=None, history=""):

    examples = retrieve_examples(question)

    sql = sql_chain.invoke({
        "question": question,
        "schema": schema,
        "examples": examples or "No examples provided.",
        "history": history or "No previous conversation."
    })

    return sql.replace("```sql", "").replace("```", "").strip()



def fix_sql(sql_query, error_message, schema):

    sql = sql_fix_chain.invoke({
        "sql": sql_query,
        "error": error_message,
        "schema": schema
    })

    return sql.replace("```sql", "").replace("```", "").strip()



def get_fallback_suggestions(question, schema, db_url=None):
    """
    Ask the LLM for 2 alternative questions + SQL queries close to the user's intent.
    Validates each generated SQL and only returns ones that pass.
    Returns a list of dicts: [{"question": ..., "sql": ...}, ...]
    """
    raw = fallback_chain.invoke({
        "question": question,
        "schema": schema,
    }).strip()


    # Parse the structured response
    suggestions = []
    for i in (1, 2):
        try:
            q_key = f"SUGGESTION_{i}_QUESTION:"
            s_key = f"SUGGESTION_{i}_SQL:"

            q_start = raw.index(q_key) + len(q_key)
            s_start = raw.index(s_key) + len(s_key)

            # Question ends at the next SUGGESTION key or SQL key
            q_end = raw.index(s_key)
            
            # SQL ends at the next SUGGESTION block or end of string
            next_key = f"SUGGESTION_{i + 1}_QUESTION:"
            s_end = raw.index(next_key) if next_key in raw else len(raw)

            alt_question = raw[q_start:q_end].strip()
            alt_sql = raw[s_start:s_end].strip().replace("```sql", "").replace("```", "").strip()


            # Validate before including
            is_valid, _ = validate_sql(alt_sql, db_url=db_url)
            if is_valid:
                suggestions.append({"question": alt_question, "sql": alt_sql})
        except (ValueError, IndexError):
            continue

    return suggestions
