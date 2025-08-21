
import uvicorn
from fastapi import FastAPI
from api.address import router as address_group
from settings import AppSettings, EnvSettings
from fastapi.middleware.cors import CORSMiddleware
# --- Security Middleware ---
# CORS Middleware: restricts which domains can access your API
# app = FastAPI(openapi_tags=AppSettings.APP_METADATA)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://your-frontend-domain.com"],  # Change to your allowed origins
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Example: Authentication Middleware (placeholder)
# from fastapi import status
# @app.middleware("http")
# async def auth_middleware(request: Request, call_next):
#     # Example: check for an Authorization header
#     if not request.headers.get("Authorization"):
#         return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Unauthorized"})
#     return await call_next(request)

# ...existing code...

# Initialize FastAPI app
app = FastAPI(openapi_tags=AppSettings.APP_METADATA)
app.title = AppSettings.APP_TIITLE
app.description = AppSettings.APP_DESCRIPTION
app.version = AppSettings.APP_VERSION

app.include_router(address_group, prefix="", tags=["Address Book Group"])

if __name__ == "__main__":
    uvicorn.run("main:app", host=EnvSettings.HOST, port=int(EnvSettings.PORT), reload=AppSettings.APP_RELOAD, timeout_keep_alive=AppSettings.APP_TIMEOUT)