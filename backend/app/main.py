from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.usuarios.router import router as usuarios_router
from app.modules.bitacora.router import router as bitacora_router


app = FastAPI(
    title="Taller API",
    description="Backend para sistema de asistencia vehicular",
    version="1.0.0"
)

# ── CORS ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────
app.include_router(usuarios_router, prefix="/api")
app.include_router(bitacora_router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok", "message": "Taller API corriendo"}


