"""API application lifecycle."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
@asynccontextmanager
async def lifespan(app:FastAPI):
    app.state.ready=True
    yield
    app.state.ready=False
