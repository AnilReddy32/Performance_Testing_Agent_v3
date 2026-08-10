from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import traceback

from Performance_Testing_Agent.config import APP_NAME,APP_VERSION 
from Performance_Testing_Agent.orchestrator.orchestrator import Orchestrator

#---------------------------------
# FASTAPI Application
#---------------------------------

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI Multi-Agent Performance Testing System"
)

#---------------------------- 
# Initialize Orchestrator
#----------------------------

orchestrator = Orchestrator()
 
#---------------------------- 
# Request Schema
#----------------------------

class UserQuery(BaseModel):
    query: str
 
#-------------------------
# Home Application
# ------------------------


@app.get("/")
async def home():
    return {
        "application": APP_NAME,
        "status": "Running",
        "version": APP_VERSION
    }
 
#Health check
@app.get("/health")
async def health():
    return{
        "status": "Healthy"
    } 

#main Endpoint

@app.post("/chat")
async def chat(request: UserQuery):
    """
    Accepts a user query and passes it to the Orchestrator.
    """
 
    try:
        result = await orchestrator.execute(request.query)
 
        return {
            "success": True,
            "data": result
        }
 
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
 
 
 
if __name__ == "__main__":
    import uvicorn
    from Performance_Testing_Agent.config import HOST,PORT
 
    uvicorn.run(
        "Performance_Testing_Agent.main:app",
        host=HOST,
        port=PORT,
        reload=True
    )