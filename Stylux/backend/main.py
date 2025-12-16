from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import requests
from typing import List, Optional
import os
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Configure the FastAPI app
app = FastAPI(
    title="STYLUX AI Fashion Assistant API",
    description="""
    AI-powered fashion recommendation chatbot API using OpenRouter AI.
    
    This API provides personalized fashion recommendations based on:
    - Skin tone
    - Color preferences
    - Style preferences (casual, formal, party, etc.)
    - Occasion
    
    The API uses OpenRouter's powerful AI models to provide natural, context-aware responses.
    """,
    version="2.0.0"
)

# CORS configuration
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
origins = allowed_origins_env.split(",") if allowed_origins_env else []
default_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "https://stylux-ai.vercel.app",
    "https://st-lux-ai.vercel.app",
    "https://stylux-ai.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + default_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Message(BaseModel):
    sender: str
    text: str
    timestamp: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Message] = []

class ChatResponse(BaseModel):
    response: str
    suggested_options: Optional[List[str]] = None

# Initialize OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not found in environment variables")
    print("Please set OPENROUTER_API_KEY in your .env file")
    OPENROUTER_API_KEY = "your_openrouter_api_key_here"

OPENROUTER_API_URL = "https://api.openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:5173",  # Replace with your actual domain in production
    "OpenAI-Organization": "org-gP0iUn5UakNSU8mQHfWoZy9S",  # Required by OpenRouter
    "X-Title": "STYLUX AI Fashion Assistant"  # Name of your application
}

def load_fashion_data() -> pd.DataFrame:
    """Load and clean fashion data from the CSV file."""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, 'final.csv')
        
        # Fallback: check current working directory if not found in script dir
        if not os.path.exists(csv_path):
            current_dir_path = os.path.join(os.getcwd(), 'final.csv')
            if os.path.exists(current_dir_path):
                csv_path = current_dir_path
                print(f"Found final.csv in current directory: {csv_path}")
            else:
                print(f"Could not find final.csv in {script_dir} or {os.getcwd()}")
        
        df = pd.read_csv(csv_path)

        # Remove unnecessary or empty columns
        df = df.drop(columns=['Unnamed: 6'], errors='ignore')

        # Drop rows with missing critical values
        df = df.dropna(subset=['skin_tone', 'recommended_outfit_(men)', 'why_this_outfit_(men)', 'shade', 'preferred_colors', 'style'])

        return df
    except FileNotFoundError:
        print(f"CSV file not found at {csv_path}")
        raise HTTPException(status_code=404, detail="Fashion data file not found")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading fashion data: {str(e)}")

def generate_prompt_from_history(conversation_history: List[Message], df: pd.DataFrame) -> str:
    """Generate a prompt for the AI model based on user history and fashion data."""
    
    # Get relevant fashion data based on user message
    user_message = conversation_history[-1].text if conversation_history else ""
    message_lower = user_message.lower()
    
    # Search for relevant outfits based on keywords
    relevant_outfits = []
    
    # Keywords for different styles and preferences
    summer_keywords = ['summer', 'hot', 'warm', 'beach', 'vacation']
    formal_keywords = ['formal', 'business', 'office', 'professional', 'work']
    party_keywords = ['party', 'celebration', 'evening', 'night', 'dress']
    casual_keywords = ['casual', 'everyday', 'comfortable', 'relaxed']
    skin_tone_keywords = ['fair', 'tan', 'medium', 'dark', 'honey', 'caramel', 'deep tan', 'warm brown', 'ebony', 'porcelain', 'light', 'beige', 'olive', 'deep dark']
    color_keywords = ['blue', 'red', 'green', 'yellow', 'black', 'white', 'brown', 'gray', 'navy', 'olive', 'burgundy', 'gold', 'silver', 'emerald', 'mustard', 'charcoal', 'cream', 'tan', 'mint', 'royal', 'sky', 'deep red', 'burnt orange']
    
    # Filter outfits based on user input
    if any(keyword in message_lower for keyword in skin_tone_keywords):
        # Find specific skin tone matches
        for skin_tone in skin_tone_keywords:
            if skin_tone in message_lower:
                relevant_outfits = df[df['skin_tone'].str.contains(skin_tone, case=False, na=False)].head(5)
                break
    elif any(keyword in message_lower for keyword in color_keywords):
        # Find color matches
        for color in color_keywords:
            if color in message_lower:
                relevant_outfits = df[df['preferred_colors'].str.contains(color, case=False, na=False) | 
                                   df['recommended_outfit_(men)'].str.contains(color, case=False, na=False)].head(5)
                break
    elif any(keyword in message_lower for keyword in summer_keywords):
        relevant_outfits = df[df['style'].str.contains('casual', case=False, na=False)].head(5)
    elif any(keyword in message_lower for keyword in formal_keywords):
        relevant_outfits = df[df['style'].str.contains('formal|business', case=False, na=False)].head(5)
    elif any(keyword in message_lower for keyword in party_keywords):
        relevant_outfits = df[df['style'].str.contains('party|evening|elegant', case=False, na=False)].head(5)
    else:
        # Get diverse suggestions if no specific matches
        relevant_outfits = df.sample(n=min(5, len(df)))
    
    # If no specific matches, get diverse suggestions
    if relevant_outfits.empty:
        relevant_outfits = df.sample(n=min(5, len(df)))
    
    # Format the fashion data for the AI
    fashion_data = "\n".join([
        f"Outfit: {outfit['recommended_outfit_(men)']} | "
        f"Skin Tone: {outfit['skin_tone']} | "
        f"Colors: {outfit['preferred_colors']} | "
        f"Style: {outfit['style']} | "
        f"Reason: {outfit['why_this_outfit_(men)']}"
        for _, outfit in relevant_outfits.iterrows()
    ])
    
    # Build conversation history
    conversation_str = "\n".join([f"{msg.sender}: {msg.text}" for msg in conversation_history])
    
    # Create a comprehensive prompt for the AI
    prompt = f"""
You are STYLUX, a friendly and knowledgeable AI fashion assistant. You help users find the perfect outfits based on their preferences, skin tone, and style needs.

Fashion Database (relevant to user's request):
{fashion_data}

Conversation History:
{conversation_str}

User's Request: {user_message}

Instructions:
1. Analyze the user's request and the fashion database above
2. Provide personalized, conversational fashion advice using the specific outfits from the database
3. Reference the exact outfits, skin tones, colors, and reasons from the database
4. Explain why each suggestion works for their specific needs
5. Be friendly, helpful, and specific about the recommendations
6. If they mention skin tone or colors, use that information to filter suggestions
7. If they don't specify preferences, suggest diverse options from the database
8. Always base your recommendations on the fashion data provided above

Please provide a natural, conversational response that references specific outfits from the database and explains why they work for the user's needs.
"""
    
    return prompt.strip()

async def generate_response_from_openrouter(prompt: str) -> str:
    """Generate a response using the OpenRouter API."""
    try:
        payload = {
            "model": "anthropic/claude-3-haiku",  # Using a more reliable model
            "messages": [
                {"role": "system", "content": "You are STYLUX, a friendly and knowledgeable AI fashion assistant specializing in personalized fashion recommendations."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000,  # Limit response length
            "stream": False  # Don't stream the response
        }
        
        response = requests.post(
            OPENROUTER_API_URL,
            headers=HEADERS,
            json=payload
        )
        
        if response.status_code == 200:
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
        else:
            print(f"OpenRouter API error: {response.status_code} - {response.text}")
            return generate_fallback_response(prompt)
            
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        return generate_fallback_response(prompt)

def generate_fallback_response(user_message: str) -> str:
    """Generate a fallback response when AI is not available."""
    try:
        df = load_fashion_data()
        # Get 3 random outfits from the dataset
        outfits = df.sample(n=3)

        # Define keywords (same as in generate_prompt_from_history)
        summer_keywords = ['summer', 'hot', 'warm', 'beach', 'vacation']
        formal_keywords = ['formal', 'business', 'office', 'professional', 'work']
        party_keywords = ['party', 'celebration', 'evening', 'night', 'dress']
        skin_tone_keywords = ['fair', 'tan', 'medium', 'dark', 'honey', 'caramel', 'deep tan', 'warm brown', 'ebony', 'porcelain', 'light', 'beige', 'olive', 'deep dark']
        color_keywords = ['blue', 'red', 'green', 'yellow', 'black', 'white', 'brown', 'gray', 'navy', 'olive', 'burgundy', 'gold', 'silver', 'emerald', 'mustard', 'charcoal', 'cream', 'tan', 'mint', 'royal', 'sky', 'deep red', 'burnt orange']

        response = ["I apologize for any issues with our AI system. Here are some fashion suggestions for you:"]
        
        # Convert user_message to lowercase for keyword matching
        message_lower = user_message.lower()
        
        # Determine the type of request
        is_summer_request = any(keyword in message_lower for keyword in summer_keywords)
        is_formal_request = any(keyword in message_lower for keyword in formal_keywords)
        is_party_request = any(keyword in message_lower for keyword in party_keywords)
        has_skin_tone = any(keyword in message_lower for keyword in skin_tone_keywords)
        has_color_preference = any(keyword in message_lower for keyword in color_keywords)
        
        # Find specific skin tone if mentioned
        specific_skin_tone = None
        for skin_tone in skin_tone_keywords:
            if skin_tone in message_lower:
                specific_skin_tone = skin_tone
                break
        
        # Find specific color if mentioned
        specific_color = None
        for color in color_keywords:
            if color in message_lower:
                specific_color = color
                break
        
        # Filter outfits based on request type and preferences
        if specific_skin_tone:
            relevant_outfits = df[df['skin_tone'].str.contains(specific_skin_tone, case=False, na=False)].head(3)
        elif specific_color:
            relevant_outfits = df[
                (df['preferred_colors'].str.contains(specific_color, case=False, na=False)) |
                (df['recommended_outfit_(men)'].str.contains(specific_color, case=False, na=False))
            ].head(3)
        elif is_summer_request:
            relevant_outfits = df[df['style'].str.contains('casual', case=False, na=False)].head(3)
        elif is_formal_request:
            relevant_outfits = df[df['style'].str.contains('formal|business', case=False, na=False)].head(3)
        elif is_party_request:
            relevant_outfits = df[df['style'].str.contains('party|evening|elegant', case=False, na=False)].head(3)
        else:
            # Get diverse suggestions
            relevant_outfits = df.sample(n=min(3, len(df)))
        
        if relevant_outfits.empty:
            relevant_outfits = df.sample(n=min(3, len(df)))
        
        # Create personalized response based on request type
        if specific_skin_tone:
            intro = f"Perfect! I found some great options for {specific_skin_tone} skin tone:"
        elif specific_color:
            intro = f"Excellent choice! Here are some stylish {specific_color} options:"
        elif is_summer_request:
            intro = "Perfect for summer! Here are some great warm-weather outfit suggestions:"
        elif is_formal_request:
            intro = "Great choice for professional settings! Here are some formal outfit recommendations:"
        elif is_party_request:
            intro = "Time to party! Here are some stylish evening outfit options:"
        else:
            intro = "Here are some fantastic fashion suggestions for you:"
        
        response_parts = [intro]
        
        # Add specific outfit recommendations with explanations
        for idx, outfit in relevant_outfits.iterrows():
            outfit_desc = f"• {outfit['recommended_outfit_(men)']} - {outfit['why_this_outfit_(men)']}"
            response_parts.append(outfit_desc)
        
        # Add personalized tip based on request
        if specific_skin_tone:
            response_parts.append(f"\n💡 Tip: These suggestions are specifically tailored for {specific_skin_tone} skin tone. For even better results, try mentioning your preferred colors too!")
        elif specific_color:
            response_parts.append(f"\n💡 Tip: Great {specific_color} choices! These suggestions complement your color preference perfectly.")
        elif has_skin_tone:
            response_parts.append("\n💡 Tip: I've considered your skin tone in these suggestions. For even better results, try mentioning your preferred colors too!")
        elif has_color_preference:
            response_parts.append("\n💡 Tip: Great color choice! These suggestions complement your preferred colors perfectly.")
        else:
            response_parts.append("\n💡 Tip: For more personalized recommendations, try mentioning your skin tone or preferred colors!")
        
        return "\n\n".join(response_parts)
        
    except Exception as e:
        print(f"Error generating fallback response: {e}")
        # Provide a basic response even if there's an error
        try:
            basic_outfits = df.head(3)
            response_parts = ["Here are some great fashion suggestions:"]
            for idx, outfit in basic_outfits.iterrows():
                outfit_desc = f"• {outfit['recommended_outfit_(men)']} - {outfit['why_this_outfit_(men)']}"
                response_parts.append(outfit_desc)
            return "\n\n".join(response_parts)
        except:
            return "Here are some great fashion suggestions:\n\n• Blue Casual Shirt - Matches fair skin tone, blue/white colors, and casual summer style.\n• Mustard Yellow Casual Shirt + Brown Pants - Fits tan skin tone, and mustard yellow/brown preferences for formal wear.\n• Red T-shirt + Black Jeans - Matches medium skin tone with red/black colors, and is great for casual wear."

def detect_greeting(user_message: str) -> bool:
    """Detect if the user message is a greeting."""
    greeting_keywords = [
        'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
        'howdy', 'greetings', 'what\'s up', 'sup', 'yo', 'good day',
        'morning', 'afternoon', 'evening', 'hi there', 'hello there'
    ]
    
    message_lower = user_message.lower().strip()
    return any(greeting in message_lower for greeting in greeting_keywords)

def detect_farewell(user_message: str) -> bool:
    """Detect if the user message is a farewell."""
    farewell_keywords = [
        'bye', 'goodbye', 'see you', 'see ya', 'take care', 'farewell',
        'good night', 'goodnight', 'have a good day', 'have a nice day',
        'thanks', 'thank you', 'thank you so much', 'thanks a lot'
    ]
    
    message_lower = user_message.lower().strip()
    return any(farewell in message_lower for farewell in farewell_keywords)

def get_greeting_response() -> str:
    """Get a friendly greeting response."""
    greetings = [
        "Hello! 👋 I'm STYLUX, your AI fashion assistant. I'm here to help you find the perfect outfits based on your style preferences, skin tone, and color choices. What would you like to know about fashion today?",
        
        "Hi there! ✨ Welcome to STYLUX - your personal fashion advisor. I can help you discover amazing outfit combinations that match your skin tone, preferred colors, and style. What's your fashion question?",
        
        "Hey! 🎨 Great to meet you! I'm STYLUX, your AI fashion companion. Whether you're looking for casual wear, formal attire, or party outfits, I've got you covered. What style are you thinking about today?",
        
        "Good day! 👔 I'm STYLUX, your fashion expert. From summer casuals to elegant evening wear, I can suggest perfect outfits that complement your skin tone and color preferences. What's on your mind?",
        
        "Hello! 🌟 Welcome to STYLUX! I'm here to be your personal stylist. I can recommend outfits based on your skin tone, favorite colors, and the occasion. What kind of look are you going for?"
    ]
    
    import random
    return random.choice(greetings)

def get_farewell_response() -> str:
    """Get a friendly farewell response."""
    farewells = [
        "You're welcome! 👋 It was great helping you with your fashion choices. Feel free to come back anytime for more style advice. Have a fabulous day!",
        
        "Thanks for chatting with me! ✨ I hope you found some great outfit ideas. Don't hesitate to return if you need more fashion inspiration. Stay stylish!",
        
        "Goodbye! 🎨 It was a pleasure being your fashion assistant today. Remember, confidence is the best accessory! Come back soon for more style tips.",
        
        "Take care! 👔 Thanks for choosing STYLUX for your fashion needs. I'm always here when you need style advice. Have a wonderful day!",
        
        "See you later! 🌟 Thanks for the chat! I hope my suggestions help you look and feel amazing. Come back anytime for more fashion guidance!"
    ]
    
    import random
    return random.choice(farewells)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for fashion recommendations."""
    try:
        print(f"Received chat request: {request.message}")
        
        # Check if it's a greeting
        if detect_greeting(request.message):
            print("Greeting detected, sending welcome message")
            return ChatResponse(
                response=get_greeting_response(),
                suggested_options=[
                    "Tell me about summer outfits",
                    "I have fair skin, what should I wear?",
                    "Show me formal business wear",
                    "I like blue colors, any suggestions?"
                ]
            )
        
        # Check if it's a farewell
        if detect_farewell(request.message):
            print("Farewell detected, sending goodbye message")
            return ChatResponse(
                response=get_farewell_response(),
                suggested_options=[
                    "Tell me about summer outfits",
                    "I have fair skin, what should I wear?",
                    "Show me formal business wear",
                    "I like blue colors, any suggestions?"
                ]
            )
        
        df = load_fashion_data()
        prompt = generate_prompt_from_history(request.conversation_history + [Message(sender="user", text=request.message, timestamp="")], df)
        
        try:
            response_text = await generate_response_from_openrouter(prompt)
        except Exception as e:
            print(f"Error generating response: {e}")
            response_text = generate_fallback_response(request.message)

        # Get suggested options from the dataset based on user message
        message_lower = request.message.lower()
        
        # Filter suggestions based on user input
        if any(keyword in message_lower for keyword in ['summer', 'hot', 'warm', 'casual']):
            suggested_df = df[df['style'].str.contains('casual', case=False, na=False)]
        elif any(keyword in message_lower for keyword in ['formal', 'business', 'office']):
            suggested_df = df[df['style'].str.contains('formal|business', case=False, na=False)]
        elif any(keyword in message_lower for keyword in ['party', 'evening', 'night']):
            suggested_df = df[df['style'].str.contains('party|evening|elegant', case=False, na=False)]
        else:
            suggested_df = df
        
        # If filtered results are empty, use all data
        if suggested_df.empty:
            suggested_df = df
            
        suggested_options = suggested_df[['recommended_outfit_(men)', 'why_this_outfit_(men)']].head(3).to_dict(orient="records")
        
        return ChatResponse(
            response=response_text,
            suggested_options=[f"{item['recommended_outfit_(men)']} - Why: {item['why_this_outfit_(men)']}" for item in suggested_options]
        )
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        # Even if there's an error, try to provide a fallback response
        try:
            response_text = generate_fallback_response(request.message)
            return ChatResponse(
                response=response_text,
                suggested_options=[
                    "Tell me about summer outfits",
                    "I have fair skin, what should I wear?",
                    "Show me formal business wear",
                    "I like blue colors, any suggestions?"
                ]
            )
        except:
            raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
async def root():
    """Root endpoint to check if API is running."""
    return {"message": "STYLUX AI Fashion Assistant API is running!"}

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    try:
        df = load_fashion_data()
        return {
            "status": "API is running",
            "data_loaded": not df.empty,
            "total_outfits": len(df),
            "skin_tones": [cat for cat in df['skin_tone'].unique() if pd.notna(cat)][:5]
        }
    except Exception as e:
        return {
            "status": "API is running but data loading failed",
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "STYLUX AI Fashion Assistant"}

if __name__ == "__main__":
    import uvicorn
    # Use PORT from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    # Bind to 0.0.0.0 to make it accessible from outside the container
    uvicorn.run(app, host="0.0.0.0", port=port)