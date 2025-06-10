from fastapi import APIRouter, Depends, UploadFile, File, Request
from fastapi.responses import JSONResponse
from ..clients.firebase.verify_token import get_current_user
from ..dependencies.dependencies import get_profile_manager

from io import BytesIO

router = APIRouter(
    prefix="/profile",
    tags=["User Profile"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/is_complete")
async def get_user_profile(
    user_id: str = Depends(get_current_user),
    manager = Depends(get_profile_manager)
):
    """Check if the current user has a profile."""
    profile = await manager.get_user_profile(user_id)
    if not profile:
        return {"status": "incomplete"}
    return {
        "status": "complete",
        "date_created": profile.get("date_created")
    }

@router.get("/data")
async def get_profile_data(
    user_id: str = Depends(get_current_user),
    manager = Depends(get_profile_manager)
):
    """Get the structured profile data for the current user."""
    profile = await manager.get_user_profile(user_id)
    if not profile or "structured_profile" not in profile:
        return JSONResponse(content={"error": "Profile not found"}, status_code=404)
    return profile["structured_profile"]

@router.post("/set_by_file")
async def set_user_profile_by_file(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
    manager = Depends(get_profile_manager)
):
    """Set user profile using a CV file upload."""
    try:
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["docx", "pdf"]:
            return JSONResponse(
                content={"error": "Unsupported file type. Only DOCX and PDF are allowed."},
                status_code=400,
            )

        stream = BytesIO(await file.read())
        result = await manager.set_user_profile_by_file(user_id, stream)
        return {"message": "Profile saved", "result": result}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/set_by_text")
async def set_user_profile_by_text(
    request: Request,
    user_id: str = Depends(get_current_user),
    manager = Depends(get_profile_manager)
):
    """Set user profile using structured JSON data from frontend complete manual form."""
    try:
        body = await request.json()
        
        profile_text_json = body.get("profile_text")
        if not profile_text_json:
            return JSONResponse(content={"error": "Missing profile_text"}, status_code=400)
        
        import json
        try:
            structured_data = json.loads(profile_text_json)
        except json.JSONDecodeError:
            return JSONResponse(content={"error": "Invalid JSON in profile_text"}, status_code=400)

        await manager.set_user_profile_by_text(user_id, structured_data)
        
        return {"message": "Profile saved"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)