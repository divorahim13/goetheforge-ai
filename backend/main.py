from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()

app = FastAPI(title="GoetheForge AI Backend")

# CORS supaya frontend nanti bisa connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", "https://placeholder.supabase.co"),
    os.getenv("SUPABASE_ANON_KEY", "placeholder")
)

@app.get("/health")
async def health():
    return {"status": "GoetheForge AI backend is running! 🚀"}

@app.get("/test-supabase")
async def test_supabase():
    try:
        res = supabase.table("users").select("*").limit(1).execute()
        return {"supabase": "connected", "sample": res.data}
    except Exception as e:
        return {"supabase": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
print("✅ Backend siap! Supabase terhubung.")
