import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth_routes import router as auth_router
from routes.eventos import router as eventos_router
from routes.asistencia import router as asistencia_router
from routes.personas import router as personas_router

app = FastAPI(title="MCC Sistema de Gestión", version="2.0")

# CORS — permitir frontend en Vercel y desarrollo local
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(auth_router)
app.include_router(eventos_router)
app.include_router(asistencia_router)
app.include_router(personas_router)


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0"}
