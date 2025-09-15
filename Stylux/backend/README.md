# Stylux AI Backend

## Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the `backend` directory (copy from `.env.example`):
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

4. Get your OpenRouter API key:
   - Visit [OpenRouter](https://openrouter.ai/)
   - Sign up and get your API key
   - Add the API key to your `.env` file

5. Start the backend server:
```bash
python start_server.py
```

The server will start on `http://localhost:8000`.

## API Endpoints

- `POST /chat`: Main endpoint for fashion recommendations
  - Request body:
    ```json
    {
      "message": "string",
      "conversation_history": [
        {
          "sender": "string",
          "text": "string",
          "timestamp": "string"
        }
      ]
    }
    ```
  - Response:
    ```json
    {
      "response": "string",
      "suggested_options": ["string"]
    }
    ```

- `GET /`: Health check endpoint
- `GET /test`: Test endpoint to verify data loading
- `GET /health`: Health check endpoint