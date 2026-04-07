from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from agents.planner_assessor import generate_learning_plan
from agents.diagnostic_srs import run_diagnostic

load_dotenv()

app = FastAPI(title="GoetheForge AI Backend - Phase 3 Active")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client dengan penanganan spasi (strip)
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", "").strip(),
    os.getenv("SUPABASE_ANON_KEY", "").strip()
)

@app.get("/health")
async def health():
    return {"status": "✅ Phase 3: Diagnostic + SRS Agent aktif!"}

@app.get("/generate-plan")
async def get_learning_plan(user_level: str = "A2", goals: str = ""):
    plan = generate_learning_plan(user_level, goals)
    return {"status": "success", "plan": plan}

# Endpoint baru Phase 3
@app.get("/diagnostic-test")
async def get_diagnostic_test(user_level: str = "A2"):
    result = run_diagnostic(user_level)
    return {
        "status": "success",
        "user_level": user_level,
        "test_questions": result["test_questions"],
        "flashcards": result["flashcards"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

print("✅ Phase 3: Diagnostic Test + SRS Agent sudah aktif!")
