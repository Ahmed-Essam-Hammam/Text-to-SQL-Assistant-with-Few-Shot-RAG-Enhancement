from langchain_core.output_parsers import StrOutputParser
from config import get_llm
from prompts import (
    sql_prompt,
    table_selector_prompt,
    answer_prompt,
    sql_fix_prompt,
    relevance_prompt,
    fallback_prompt,
)

llm = get_llm()

sql_chain = sql_prompt | llm | StrOutputParser()
answer_chain = answer_prompt | llm | StrOutputParser()
table_selector_chain = table_selector_prompt | llm | StrOutputParser()
sql_fix_chain = sql_fix_prompt | llm | StrOutputParser()
relevance_chain = relevance_prompt | llm | StrOutputParser()
fallback_chain = fallback_prompt | llm | StrOutputParser()


INJECTION_SIGNALS = {"jailbreak", "content_filter", "prompt triggering", "ResponsibleAIPolicyViolation"}


def is_injection_error(error: Exception) -> bool:
    """Check if the error is Azure's content filter blocking a prompt injection attempt."""
    error_text = str(error).lower()
    return any(signal.lower() in error_text for signal in INJECTION_SIGNALS)


def safe_invoke(chain, inputs: dict, fallback: str = "__INJECTION__"):
    """Invoke a chain and return a fallback string if Azure flags it as a jailbreak."""
    try:
        return chain.invoke(inputs)
    except Exception as e:
        if is_injection_error(e):
            return fallback
        raise  # re-raise anything else so real errors still surface
