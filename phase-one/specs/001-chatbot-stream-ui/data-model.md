# Data Model: AI Book Assistant Chatbot

## Entities

### Chat Message
- **id**: String (unique identifier for the message)
- **text**: String (the content of the message)
- **userId**: String (identifier for the user or "ai" for system responses)
- **timestamp**: Date/Time (when the message was created)
- **messageType**: Enum (user | ai | system)
- **context**: Object (optional context information, such as selected text)
- **status**: Enum (sending | sent | failed | read)

### User Query
- **id**: String (unique identifier for the query)
- **content**: String (the text of the user's question)
- **context**: Object (optional context like selected text on the page)
- **timestamp**: Date/Time (when the query was submitted)
- **pageUrl**: String (URL of the page where query was made, for context)
- **selectedText**: String (optional selected text that provides context)

### AI Response
- **id**: String (unique identifier for the response)
- **content**: String (the AI's response text)
- **queryId**: String (reference to the original query)
- **timestamp**: Date/Time (when the response was received)
- **confidence**: Number (optional confidence score from AI service)
- **sources**: Array (optional references to book content that informed the response)

### Conversation Session
- **id**: String (unique identifier for the conversation session)
- **userId**: String (user identifier, may be anonymous)
- **startTime**: Date/Time (when the conversation started)
- **lastActivity**: Date/Time (last message timestamp)
- **messages**: Array (list of Chat Message entities)
- **status**: Enum (active | archived | expired)

## Relationships
- One Conversation Session contains many Chat Messages
- One User Query generates one AI Response
- One Chat Message may have optional Context from page selection

## Validation Rules
- Chat Message text must be 1-2000 characters
- User Query content must not be empty
- AI Response must be received within 30 seconds of query
- Conversation Session must not exceed 100 messages without archival
- Selected text context must be less than 500 characters

## State Transitions
- Chat Message: sending → sent | failed
- Conversation Session: active → archived | expired
- User Query: submitted → processing → completed | failed