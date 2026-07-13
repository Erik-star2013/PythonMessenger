README_CONTENT = """
# PythonMessenger

A modern desktop messenger application built with Python, Flet, FastAPI, WebSockets, and SQLite.

## Features

- User registration and login with JWT authentication
- Real-time messaging via WebSockets
- User search
- Message history
- Online/offline status
- Typing indicators
- Emoji avatars
- Modern Telegram-like UI
- Dark/Light theme support
- Automatic WebSocket reconnection
- Message read receipts
- Message editing and deletion

## Project Structure

```
PythonMessenger/
├── server.py                 # FastAPI server
├── main.py                  # Flet desktop client entry point
├── config.py                # Configuration constants
├── database.py              # SQLAlchemy database setup
├── models.py                # Pydantic data models
├── auth.py                  # Authentication manager
├── security.py              # JWT and password security
├── websocket_server.py      # WebSocket connection manager
├── logger.py                # Logging configuration
├── requirements.txt         # Python dependencies
├── ui/
│   ├── app.py              # Main Flet application
│   ├── login.py            # Login screen
│   ├── register.py         # Registration screen
│   ├── chat.py             # Chat window
│   └── components.py       # Reusable UI components
├── network/
│   ├── client.py           # HTTP API client
│   └── websocket.py        # WebSocket client
└── README.md
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PythonMessenger.git
cd PythonMessenger
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Terminal 1 - Start the FastAPI Server

```bash
uvicorn server:app --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Terminal 2 - Start the Flet Desktop Client

```bash
python main.py
```

The desktop messenger window will open.

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

### Users

- `GET /api/users/search` - Search for users
- `GET /api/users/{user_id}` - Get user info

### Messages

- `GET /api/messages/{user_id}` - Get message history
- `GET /api/chats` - Get recent chats

### Health

- `GET /api/health` - Server health check

### WebSocket

- `WS /ws/{token}` - Real-time messaging connection

## Usage

1. Open the application
2. Register a new account or login with existing credentials
3. Search for users using the search bar
4. Click on a user to open the chat
5. Type a message and click Send or press Enter+Shift
6. Messages are sent in real-time via WebSocket

## Configuration

Edit `config.py` to customize:

- Server host/port
- Database URL
- Maximum message length
- Avatar emoji list
- And more...

## Database

The application uses SQLite with SQLAlchemy ORM.

Database file: `messenger.db` (created automatically)

### Schema

- **Users Table**: Stores user information, passwords (hashed), avatars, online status
- **Messages Table**: Stores all messages between users, message status, timestamps

## Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- WebSocket connections require valid tokens
- Input validation on all endpoints
- SQL injection prevention via SQLAlchemy ORM

## Development

### Running in development mode:

```bash
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

### Logs

Logs are saved to `logs/messenger.log` and also printed to console.

## Troubleshooting

### "Cannot connect to server"

Make sure the server is running in Terminal 1:
```bash
uvicorn server:app --host 127.0.0.1 --port 8000
```

### "Connection refused"

Check that port 8000 is not in use by another application.

### "Module not found" errors

Re-install dependencies:
```bash
pip install -r requirements.txt
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License

## Support

For support, open an issue on GitHub or contact the maintainers.

## Acknowledgments

- Built with [Flet](https://flet.dev/) - Python UI framework
- Backend powered by [FastAPI](https://fastapi.tiangolo.com/)
- Real-time communication with [WebSockets](https://websockets.readthedocs.io/)
- Database management with [SQLAlchemy](https://www.sqlalchemy.org/)
"""

if __name__ == "__main__":
    print(README_CONTENT)
