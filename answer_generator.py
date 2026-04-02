from chains import answer_chain


def get_natural_response(question, data, history, is_limited=False):
    return answer_chain.invoke({
        "question": question,
        "data": data,
        "is_limited": str(is_limited),
        "history": history or "No previous conversation."
    }).strip()
