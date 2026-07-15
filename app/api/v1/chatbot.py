import json
from fastapi import APIRouter, Depends, HTTPException
import openai
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chatbot import ChatRequest
from app.config import settings
from app.services.chatbot import search_local_pois, get_community_reviews

router = APIRouter()

# 2. Define JSON schemas of tools for OpenAI
CHATBOT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_local_pois",
            "description": "Find official attractions, restaurants, shopping, or cultural spots in Seoul from our database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_name": {
                        "type": "string",
                        "description": "The category of the place. One of: '관광지', '문화시설', '축제공연행사', '여행코스', '레포츠', '숙박', '쇼핑'"
                    },
                    "query_location": {
                        "type": "string",
                        "description": "Specific district, neighborhood, or street in Korean (e.g., '강남구', '동교동')."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_community_reviews",
            "description": "Retrieve anonymous community posts and reviews written by other users for a category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_name": {
                        "type": "string",
                        "description": "The category of the place. One of: '관광지', '문화시설', '축제공연행사', '여행코스', '레포츠', '숙박', '쇼핑'"
                    },
                },
                "required": ["category_name"]
            }
        }
    }
]

@router.post("/chat")
async def handle_chat(payload: ChatRequest, db: Session = Depends(get_db)):
    client = openai.OpenAI(api_key=settings.openai_api_key)
    
    messages = [
        {"role": "system", "content": (
            "You are a local Seoul guide assistant. Use database tools to fetch official spots and community posts before answering.\n\n"
            "CRITICAL RULES:\n"
            "1. Respond in Korean. Always use polite language.\n"
            "2. If the user's request is irrelevant to Seoul tourism, local spots, or reviews (e.g., math, general coding, random chatting), "
            "do NOT call any database tools. Instead, politely decline the request and explicitly guide them to ask about your features. "
        )},
        {"role": "user", "content": payload.message}
    ]
    
    # Send user message and tool specs to OpenAI
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
        tools=CHATBOT_TOOLS,
        tool_choice="auto"
    )
    
    response_msg = response.choices[0].message
    
    # If OpenAI determines it needs database data
    if response_msg.tool_calls:
        messages.append(response_msg)
        
        for tool_call in response_msg.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            db_data = []
            if func_name == "search_local_pois":
                db_data = search_local_pois(
                    db, 
                    category_name=args.get("category_name"), 
                    query_location=args.get("query_location")
                )
            elif func_name == "get_community_reviews":
                db_data = get_community_reviews(db, category_name=args.get("category_name"))
            
            # Send the database query results back as a tool message
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": func_name,
                "content": json.dumps(db_data, ensure_ascii=False)
            })
            
        # Call OpenAI again with the newly retrieved DB context
        final_response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages
        )
        return {"response": final_response.choices[0].message.content}
        
    return {"response": response_msg.content}