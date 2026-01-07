# Data Model: AI Book Assistant (ChatKit-based)

## Entities

### Chat Session
- **id**: String (unique identifier for the session)
- **startTime**: Date/Time (when the session started)
- **lastActivity**: Date/Time (timestamp of last interaction)
- **status**: Enum (active | inactive | archived)
- **messages**: Array (list of Message entities in this session)

### Message
- **id**: String (unique identifier for the message)
- **content**: String (the text content of the message)
- **sender**: Enum (user | ai | system)
- **timestamp**: Date/Time (when the message was created)
- **status**: Enum (sending | sent | failed | read)
- **context**: Object (optional context information like selected text)

### User Query
- **id**: String (unique identifier for the query)
- **text**: String (the user's question or input)
- **selectedTextContext**: String (optional selected text that provides context)
- **timestamp**: Date/Time (when the query was submitted)
- **pageUrl**: String (URL of the page where query was made)

### AI Response
- **id**: String (unique identifier for the response)
- **text**: String (the AI's response text)
- **queryId**: String (reference to the original query)
- **timestamp**: Date/Time (when the response was received)
- **sources**: Array (optional references to book content that informed the response)

### Selected Text Context
- **id**: String (unique identifier)
- **text**: String (the highlighted text)
- **pageUrl**: String (URL of the page where text was selected)
- **timestamp**: Date/Time (when text was selected)
- **length**: Number (character count of the selected text)

## Relationships
- One Chat Session contains many Messages
- One User Query generates one AI Response
- One Selected Text Context may be associated with one User Query
- One Message may have optional Selected Text Context

## Validation Rules
- Message content must be 1-2000 characters
- User Query text must not be empty
- Selected Text Context must be less than 500 characters
- Chat Session must not exceed 100 messages without archival
- AI Response must be received within 30 seconds of query

## State Transitions
- Chat Session: active → inactive | archived
- Message: sending → sent | failed
- User Query: submitted → processing → completed | failed