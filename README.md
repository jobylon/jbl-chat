# Chat app

This is a simple chat backend implemented as a RESTful API. It supports conversations between two or more users. The app uses basic HTTP authentication, and each request must be authenticated, or else a 401 error is returned.

The following API endpoints are available:

- `GET /chat/users` - list all users
- `GET /chat/conversations` - list all conversations where the authenticated user is a participant
- `POST /chat/conversations` - create a new conversation with the users specified in the request JSON
- `GET /chat/conversation/{conv_id}/messages` - get all messages from the specified conversation
- `POST /chat/converstaion/{conv_id}/messages` - post a new message to the specified conversation

## Example

Let's assume we have three users: Alice (id 1), Bob (id 2) and Clive (id 3).

If Alice wants to send a message to Bob, she must first create a conversation between them:

```
POST /chat/conversations
{
    "participants": [1, 2]
}
```

This will return a new conversation:

```
{
    "id": 15,
    "participants": [1, 2]
}
```

She can now send a message to the new conversation:

```
POST /chat/conversation/15/message
{
    "text": "Hello there Bob"
}
```

And Bob can receive the messages from the conversation:

```
GET /chat/conversation/15/message
```

Response:

```
{
    "sender": 1,
    "timestamp": "2022-06-21T17:09:38.058221Z"
    "text": "Hello there Bob",
    "conversation": 15
}
```

If Clive attempts to read (or send a message to) their conversation, he will receive an error:

```
GET /chat/conversation/15/message
```

Response:

```
{
    "error": "conversation not found"
}
```

If attempting to create a conversation that already exists (i.e. a conversation with the same users), a conflict error is returned:

```
POST /chat/conversations
{
    "participants": [1, 2]
}
```

Response:

```
{
    "error": "conversation already exists",
    "conflicting_id": 15
}
```
