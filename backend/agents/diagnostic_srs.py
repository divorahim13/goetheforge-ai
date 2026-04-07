from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import json
from supabase import create_client, Client

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Supabase client dengan penanganan spasi (strip)
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", "").strip(),
    os.getenv("SUPABASE_ANON_KEY", "").strip()
)

class DiagnosticState(TypedDict):
    user_level: str
    test_questions: str
    user_answers: list
    score: int
    feedback: str
    flashcards: list

diagnostic_prompt = ChatPromptTemplate.from_template("""
Kamu adalah penguji resmi Goethe-Institut.
Buatkan 10 soal diagnostik level {user_level} sampai B1.
Topik: grammar (cases, verb conjugation, articles) + vocab sehari-hari + kalimat sederhana.
Format JSON array:
[
  {{"id":1, "question":"...", "options":["A. ...", "B. ..."], "correct":"A"}}
]
Jawab HANYA JSON, tidak ada teks lain.
""")

srs_prompt = ChatPromptTemplate.from_template("""
Buatkan 15 flashcard SRS untuk level B2 Goethe.
Setiap card: German word/phrase, contoh kalimat natural, terjemahan Indonesia, grammar note kalau perlu.
Output JSON array:
[
  {{"word":"...", "example":"...", "translation":"...", "note":"..."}}
]
Jawab HANYA JSON.
""")

def generate_diagnostic_test(state: DiagnosticState) -> DiagnosticState:
    prompt = diagnostic_prompt.invoke({"user_level": state["user_level"]})
    response = llm.invoke(prompt)
    # Gunakan json.loads untuk memproses string JSON dari LLM
    try:
        # Bersihkan response jika ada Markdown code blocks
        content = response.content.replace("```json", "").replace("```", "").strip()
        state["test_questions"] = content
    except Exception as e:
        state["test_questions"] = "[]"
    return state

def generate_srs_flashcards(state: DiagnosticState) -> DiagnosticState:
    prompt = srs_prompt.invoke({})
    response = llm.invoke(prompt)
    try:
        content = response.content.replace("```json", "").replace("```", "").strip()
        state["flashcards"] = json.loads(content)
    except Exception as e:
        state["flashcards"] = []
    return state

def save_test_result(state: DiagnosticState) -> DiagnosticState:
    try:
        supabase.table("user_progress").insert({
            "user_id": "demo_user",
            "test_type": "diagnostic",
            "score": state.get("score", 0),
            "total_questions": 10,
            "details": {"questions": state.get("test_questions"), "answers": state.get("user_answers")}
        }).execute()
    except Exception as e:
        print(f"Error saving to Supabase: {e}")
    return state

def create_diagnostic_graph():
    workflow = StateGraph(DiagnosticState)
    workflow.add_node("generate_test", generate_diagnostic_test)
    workflow.add_node("generate_srs", generate_srs_flashcards)
    workflow.add_node("save_result", save_test_result)
    workflow.set_entry_point("generate_test")
    workflow.add_edge("generate_test", "generate_srs")
    workflow.add_edge("generate_srs", "save_result")
    workflow.add_edge("save_result", END)
    return workflow.compile()

diagnostic_graph = create_diagnostic_graph()

# Function untuk FastAPI
def run_diagnostic(user_level: str = "A2"):
    initial_state = DiagnosticState(
        user_level=user_level,
        test_questions="",
        user_answers=[],
        score=0,
        feedback="",
        flashcards=[]
    )
    result = diagnostic_graph.invoke(initial_state)
    return {
        "test_questions": result.get("test_questions", "[]"),
        "flashcards": result.get("flashcards", [])
    }
