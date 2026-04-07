from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

# Pilih LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

class AgentState(TypedDict):
    user_level: str                  # contoh: "A2"
    target_level: str                # "B2"
    current_date: str
    goals: str
    weaknesses: list[str]
    learning_plan: str               # output akhir
    daily_plan: str

# Prompt untuk Agent Planner & Assessor
planner_prompt = ChatPromptTemplate.from_template("""
Kamu adalah Tutor Jerman Profesional Goethe-Institut.
User saat ini level: {user_level}
Target: {target_level} dalam waktu sesingkat mungkin.

Buatkan:
1. Roadmap keseluruhan (berapa minggu, fokus tiap skill: Lesen, Hören, Schreiben, Sprechen)
2. Daily plan untuk 7 hari ke depan (2-3 jam/hari)
3. Top 3 kelemahan yang harus diatasi dulu
4. Rekomendasi vocab & grammar prioritas

Jawab dalam bahasa Indonesia yang ramah dan motivasi.
User input: {goals}
""")

def planner_assessor_node(state: AgentState) -> AgentState:
    prompt = planner_prompt.invoke({
        "user_level": state.get("user_level", "A2"),
        "target_level": state.get("target_level", "B2"),
        "goals": state.get("goals", "Mau cepat B2 Goethe dengan nilai tinggi")
    })
    
    response = llm.invoke(prompt)
    
    state["learning_plan"] = response.content
    state["daily_plan"] = "7 hari ke depan akan di-generate otomatis berdasarkan plan di atas."
    return state

# Buat Graph (orchestrator)
def create_planner_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("planner_assessor", planner_assessor_node)
    workflow.set_entry_point("planner_assessor")
    workflow.add_edge("planner_assessor", END)
    return workflow.compile()

planner_graph = create_planner_graph()

# Function yang nanti dipanggil dari FastAPI
def generate_learning_plan(user_level: str = "A2", goals: str = ""):
    initial_state = AgentState(
        user_level=user_level,
        target_level="B2",
        current_date="2026-04-08",
        goals=goals,
        weaknesses=[],
        learning_plan="",
        daily_plan=""
    )
    result = planner_graph.invoke(initial_state)
    return result["learning_plan"]
