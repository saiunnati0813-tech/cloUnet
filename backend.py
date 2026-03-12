from typing import TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),  
    temperature=0.2
)


class State(TypedDict):
    question: str
    answer: str


def cncc_agent(state: State):

    prompt = f"""
You are an expert tutor for Computer Networks and Cloud Computing.

Rules:
- NO paragraphs at all
- Every single line must be a bullet point
- Keep each point short — max 1 line
- Use simple words a student can understand
- No long sentences

Use EXACTLY this structure:

**📚 Subject:** (Computer Networks or Cloud Computing)

**🔖 Topic:** (topic name)

**📖 Explanation:**
– (point 1)
– (point 2)
– (point 3)
– (point 4)
– (point 5)
– (point 6)
– (point 7)
– (point 8)

**📌 Key Points:**
– (point 1)
– (point 2)
– (point 3)
– (point 4)
– (point 5)

**💡 Example:**
– (point 1)
– (point 2)

**📝 Summary:**
– (point 1)
– (point 2)

Strictly follow this format. No paragraphs. No extra text.

Question:
{state["question"]}
"""

    response = llm.invoke(prompt)

    return {"answer": response.content}


graph = StateGraph(State)
graph.add_node("cncc_agent", cncc_agent)
graph.add_edge(START, "cncc_agent")
graph.add_edge("cncc_agent", END)


chatbot = graph.compile()
