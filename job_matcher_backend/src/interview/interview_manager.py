from openai import AsyncOpenAI
import os
from ..clients.firestore.interviews_firestore import InterviewsManager

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
interviews_manager = InterviewsManager()

SYSTEM_PROMPT = {
    "role": "system", 
    "content": """You are a professional interview coach. Your role is to:
    1. Conduct mock interviews based on the user's target job description
    2. Ask one question at a time
    3. After each answer, provide specific feedback on the user's response
    4. Offer suggestions for improvement
    5. Teach interview techniques and best practices
    6. Continue until all key competencies are covered
    7. End with a comprehensive summary.

    Make sure you start the conversation with a warm greeting and an introduction and then the first question.
    
    This is the user's target job description:
    """
}

async def initiate_chat(user_id: str, job_id: str, job_title: str, job_description: str) -> dict:
    """Start a new interview session and return the first AI response."""
    messages = [
        SYSTEM_PROMPT,
        {"role": "user", "content": job_description}
    ]

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )

    ai_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": ai_reply})

    interview_id = await interviews_manager.create_interview(
        user_id=user_id,
        job_id=job_id,
        job_title=job_title,
        messages=messages
    )
    
    return {"interview_id": interview_id, "ai_response": ai_reply}

async def continue_chat(user_id: str, interview_id: str, user_message: str) -> str:
    """Continue an interview session with a new user message."""
    messages = await interviews_manager.load_messages(user_id, interview_id)

    if not messages:
        raise ValueError("Conversation not initialized. Please initiate first.")

    messages.append({"role": "user", "content": user_message})

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )

    ai_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": ai_reply})

    await interviews_manager.save_messages(user_id, interview_id, messages)
    return ai_reply

async def get_interviews_for_user(user_id: str) -> list:
    """Get all interviews for a user."""
    return await interviews_manager.get_user_interviews(user_id)

async def load_interview_messages(user_id: str, interview_id: str) -> list:
    """Load all messages for a specific interview."""
    return await interviews_manager.load_messages(user_id, interview_id)

async def delete_interview(user_id: str, interview_id: str):
    """Delete an interview and its messages"""
    try:
        await interviews_manager.delete_interview(user_id, interview_id)
        return True
    except Exception as e:
        raise ValueError(f"Error deleting interview: {str(e)}")