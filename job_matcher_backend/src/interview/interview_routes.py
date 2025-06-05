from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from .interview_manager import (
    initiate_chat,
    continue_chat,
    get_interviews_for_user,
    load_interview_messages,
    delete_interview
)
from ..clients.firebase.verify_token import get_current_user
from pydantic import BaseModel
from ..dependencies.dependencies import get_interviews_manager, get_openai_clean_client

class InitiateInterviewRequest(BaseModel):
    job_description: str
    job_title: str

class ContinueInterviewRequest(BaseModel):
    user_message: str

router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/initiate/{job_id}")
async def api_initiate_interview(
    job_id: str,
    request: InitiateInterviewRequest,
    user_id: str = Depends(get_current_user),
    interviews_manager = Depends(get_interviews_manager),
    openai_client = Depends(get_openai_clean_client)
):
    """Start a new interview session."""
    try:
        result = await initiate_chat(
            user_id, job_id, request.job_title, request.job_description, interviews_manager, openai_client
        )
        return JSONResponse(content={
            "message": "Interview session started",
            "interview_id": result["interview_id"],
            "ai_response": result["ai_response"]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/continue/{interview_id}")
async def api_continue_interview(
    interview_id: str,
    request: ContinueInterviewRequest,
    user_id: str = Depends(get_current_user),
    interviews_manager = Depends(get_interviews_manager),
    openai_client = Depends(get_openai_clean_client)
):
    """Continue an interview session with a user message."""
    try:
        ai_response = await continue_chat(
            user_id, interview_id, request.user_message, interviews_manager, openai_client
        )
        return JSONResponse(content={
            "message": "Interview progressed",
            "ai_response": ai_response
        })
    except ValueError as e:
        if "not initialized" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
async def api_get_user_interviews(
    user_id: str = Depends(get_current_user),
    interviews_manager = Depends(get_interviews_manager)
):
    """Get all interviews for the current user."""
    try:
        interviews = await get_interviews_for_user(user_id, interviews_manager)
        return JSONResponse(content={"interviews": interviews})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages/{interview_id}")
async def api_load_messages(
    interview_id: str,
    user_id: str = Depends(get_current_user),
    interviews_manager = Depends(get_interviews_manager)
):
    """Load all messages for a specific interview."""
    try:
        messages = await load_interview_messages(user_id, interview_id, interviews_manager)
        return JSONResponse(content={"messages": messages})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{interview_id}")
async def api_delete_interview(
    interview_id: str,
    user_id: str = Depends(get_current_user),
    interviews_manager = Depends(get_interviews_manager)
):
    """Delete an interview and its messages."""
    try:
        success = await delete_interview(user_id, interview_id, interviews_manager)
        if success:
            return JSONResponse(content={"message": "Interview deleted successfully"})
        raise HTTPException(status_code=500, detail="Failed to delete interview")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))