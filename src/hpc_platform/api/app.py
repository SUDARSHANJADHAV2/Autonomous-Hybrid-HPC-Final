from __future__ import annotations

import os
from fastapi import FastAPI

from ..config.settings import Settings
from ..storage.db import DB


settings = Settings()
db = DB(settings.db_path)
app = FastAPI(title="Autonomous Hybrid HPC API", version="1.1.0")


@app.get("/healthz")
def healthz():
    return {"status": "ok", "mode": settings.mode, "automation": settings.automation_mode}


@app.get("/incidents")
def incidents():
    return db.incidents()


# Mutation endpoints are deliberately absent until authentication/authorization is configured.
# This avoids exposing unauthenticated Slurm/cloud control over the HTTP surface.
