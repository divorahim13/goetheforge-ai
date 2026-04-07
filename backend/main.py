from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from agents.planner_assessor import generate_learning_plan

load_dotenv()

app = FastAPI(title="GoetheForge AI Backend")

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
    return {"status": "GoetheForge AI backend is running! 🚀 Phase 2 active"}

@app.get("/test-supabase")
async def test_supabase():
    try:
        res = supabase.table("users").select("*").limit(1).execute()
        return {"supabase": "connected"}
    except Exception as e:
        return {"supabase": "error", "message": str(e)}

# Endpoint baru Phase 2
@app.get("/generate-plan")
async def get_learning_plan(user_level: str = "A2", goals: str = ""):
    plan = generate_learning_plan(user_level, goals)
    return {
        "status": "success",
        "user_level": user_level,
        "plan": plan
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

print("✅ Phase 2: LangGraph + Planner Agent sudah aktif!")
