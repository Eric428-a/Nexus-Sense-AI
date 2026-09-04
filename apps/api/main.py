"""FastAPI application entrypoint."""
from fastapi import FastAPI
from nexus.api.routes import health,intelligence,research,documents,agents,reports
from apps.api.lifespan import lifespan
app=FastAPI(title="NEXUS-SENSE AI",version="0.1.0",lifespan=lifespan)
for router in [health.router,intelligence.router,research.router,documents.router,agents.router,reports.router]: app.include_router(router,prefix="/api/v1")
@app.get("/")
async def root(): return {"name":"NEXUS-SENSE AI","status":"online"}
