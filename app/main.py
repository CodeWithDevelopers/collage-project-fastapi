from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGO_DETAILS, DATABASE_NAME
from app.routers import auth
from app.routers.summary import router as summary_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.dependencies.auth import get_current_user

# Create FastAPI app instance
app = FastAPI(
    title="Your API",
    description="Secure API with JWT Auth",
    version="1.0.0",
    swagger_ui_init_oauth={"usePkceWithAuthorizationCodeGrant": False},
)

# CORS configuration for allowing requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["*"] for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional OAuth2PasswordBearer (to add token auth in Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Global variable for MongoDB client
db_client = None

# MongoDB connection setup
@app.on_event("startup")
async def startup_db_client():
    global db_client
    db_client = AsyncIOMotorClient(MONGO_DETAILS)
    app.state.db = db_client[DATABASE_NAME]
    print("Connected to MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    global db_client
    db_client.close()
    print("Disconnected from MongoDB")

# Include authentication routes for login, register, etc.
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include summarization routes with JWT authentication
app.include_router(summary_router, prefix="/api/summary", tags=["Summary"])

# Test route for checking the API's status and JWT token validation
@app.get("/status")
async def get_status(current_user: dict = Depends(get_current_user)):
    return {"status": "API is running", "user": current_user["username"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
