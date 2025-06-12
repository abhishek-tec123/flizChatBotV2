# FlizChatBot

A sophisticated chatbot system that provides information about vehicles and equipment from various companies. The system uses natural language processing and vector embeddings to understand and respond to user queries about vehicle and equipment details.

## Features

- Query vehicle lists and details from delivery companies
- Query equipment lists and details from renter companies
- Natural language processing using Groq's LLM
- Vector-based semantic search for function retrieval
- RESTful API endpoints for easy integration

## Prerequisites

- Python 3.8 or higher
- GROQ API key (for LLM functionality)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd flizChatBot
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your GROQ API key:
```
GROQ_API_KEY=your_api_key_here
```

## Project Structure

```
flizChatBot/
├── src/
│   ├── app.py              # FastAPI application and endpoints
│   ├── context.py          # LLM context and response generation
│   ├── retrever.py         # Function retrieval and vector search
│   ├── api_function.py     # API functions for data retrieval
│   ├── function.txt        # Function definitions and descriptions
│   └── fun_Vector_DB/      # Vector database for function retrieval
├── requirements.txt        # Project dependencies
└── README.md              # Project documentation
```

## Usage

1. Start the FastAPI server:
```bash
uvicorn src.app:app --reload
```

2. The API will be available at `http://localhost:8000`

3. Available Endpoints:
   - POST `/query`: Submit natural language queries about vehicles and equipment

Example query:
```json
{
    "query": "show vehicle details of PTL from company XYZ"
}
```

## API Response Format

The API returns responses in the following format:
```json
{
    "function_called": "function_name",
    "generated_response": "Natural language response about the requested information"
}
```

## Error Handling

The API includes comprehensive error handling for:
- Invalid company names
- Invalid vehicle/equipment types
- Missing or invalid API keys
- Malformed queries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

## Support

For support, please [add contact information or support channels] 