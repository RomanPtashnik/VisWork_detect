from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from web.routers import auth, employees
import os
security = HTTPBearer()

app = FastAPI(
    title="Face Recognition System API",
    version="1.0",
    swagger_ui_parameters={"persistAuthorization": True}
)

from fastapi.openapi.utils import get_openapi
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Face Recognition System API",
        version="1.0",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
app = FastAPI(title="Face Recognition System API", version="1.0")

app.include_router(auth.router)
app.include_router(employees.router)

frontend_path = os.path.join(os.path.dirname(__file__), "..", "web_frontend")
frontend_path = os.path.abspath(frontend_path)
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse(os.path.join(frontend_path, "index.html"))


