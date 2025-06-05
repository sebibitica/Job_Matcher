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
    """Set user profile using structured text data."""
    try:
        body = await request.json()
        profile_data = body.get("profile_data", {})
        if not profile_data:
            return JSONResponse(content={"error": "Missing profile_data"}, status_code=400)

        sections = []

        if experience := profile_data.get("experience"):
            sections.append("Experience:\n" + "\n".join(f"- {e}" for e in experience))

        if skills := profile_data.get("skills"):
            sections.append("Skills:\n" + ", ".join(skills))

        if education := profile_data.get("education"):
            sections.append("Education:\n" + "\n".join(f"- {e}" for e in education))

        profile_text = "\n\n".join(sections)

        result = await manager.set_user_profile_by_text(user_id, profile_text)
        return {"message": "Profile saved", "result": result}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)