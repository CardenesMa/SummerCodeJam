# Transaction Architecture

## Near-final Command Designs:

### Client:

#### Initial Handshake (Client -> Server)

```ts
{
    "action": "CONNECT",
    "payload": {
        "has_record": boolean,
        @if has_record==true
        "publicId": string,
        "privateId": string,
        "publicId": string,
        @endif
    }
}
```
### Create Lobby (Client -> Server)

```ts
{
    "action": "CREATE_LOBBY",
    "payload": {
        "private_id": string,
        "public_name": string,
    }
}
```
### Join Lobby (Client -> Server)

```ts
{
    "action": "JOIN_LOBBY",
    "payload": {
        "lobby_id": string,
        "private_id": string,
        "public_name": string,
    }
}
```

### Request Game Start (Client -> Server)

```ts
{
    "action": "START_GAME",
    "payload": {
        "lobby_id": string,
        "private_id": string,
    }
}
```

### Send Sentence (Client -> Server)

```ts
{
    "action": "SUBMIT_SENTENCE",
    "payload": {
        "sentence": string,
        "private_id": string,
    }
}
```

### Send Vote (Client -> Server)

```ts
{
    "action": "SUBMIT_VOTE",
    "payload": {
        "public_id": string, (public id of the person bein voted for)
        "private_id": string, (private id of the person voting)
    }
}
```

## Special Data Types

### lobbyUser Type (data) Similar to above

```ts
type lobbyUser = {
    "public_id": string,
    "public_name": string,
}
```

```ts
type sentence = {
    "public_id": string, // id of the user that submitted this sentence
    "public_name": Optional<string>, // if possible
    "text": string,
}
```

```ts
type sentenceResults = {
    "public_id": string, // id of the user that submitted this sentence
    "public_name": Optional<string>,
    "text": string, // possibly optional
    "votes": number,
}
```

```ts
type gameResult = {
    "public_id": string,
    "public_name": Optional<string>,
    "score": number,
}
```

## Server

### User Info (Server -> Client)
```ts
{
    "action": "USER_INFO",
    "payload": {
        "public_id": string,
        "private_id": string,
    }
}
```



### Lobby Join (Server -> Client)
```ts
{
    "action": "ACK_JOIN",
    "payload": {
        "users": Array<lobbyUser>,
        "lobby_id": string,
    }
}
```

### User Connect (Server -> Client)
```ts
{
    "action": "USER_CONNECT",
    "payload": {"user": lobbyUser}
}
```

### User Disconnect (Server -> Client)
```ts
{
    "action": "USER_DISCONNECT",
    "payload": lobbyUser
}
```

### Send Prompt (Server -> Client)
```ts
{
    "action" : "SEND_PROMPT",
    "payload": {
        "prompt": string,
        "limit": Optional<number> // time in seconds to fill out prompt
    }
}
```


### Send All User Sentences  (Server -> Client)
```ts
{
    "action": "SEND_SENT",
    "payload": {
        "prompt": string,
        "sentences": Array<sentence> // time in seconds to vote
    }
}
```



### Send Round Results (Server -> Client)
```ts
{
    "action" : "ROUND_RES",
    "payload": {
        "winning_sent": sentenceResult,
        "other_sents": Array<sentenceResult>
    }
}
```

### Send Game Result (Server -> Client)
```ts
{
    "action": "GAME_RES",
    "payload": {
        "scores": Array<gameResult>
    }
}
```


### Typical transaction


```uml
Server                                   Client
|                                           |
|  <----  initial handshake ---             |
|                                           |
|   --- if client had no private ids  ----- |
|   --------     User Info       ----->     |
|   --------------------------------------- |
|                                           |
|   ---------- Either -------------------   |
|   <----      Join Lobby   ---------       |
|   <----      Create Lobby ---------       |
|   --------------------------------------- |
|                                           |
|   -------     Lobby Join  ------->        |
|                                           |
|   -------- n times after join ----------- |
|   -------  User Connect --------->        |
|   -------  User Disconnect ------->       |
|   --------------------------------------  |
|                                           |
|   ------------ One of the users --------- |
|   <-------    Request Game Start -------- |
|   --------------------------------------- |
|                                           |
|   -------  Send Prompt    ----->          |
|                                           |
|   ------- before x1 seconds  ------------ |
|   <------- Send Sentence -------          |
|   --------------------------------------- |
|                                           |
|   -------- after x1 seconds    ---------  |
|   -------  Send All User Sentences ---->  |
|   --------------------------------------  |
|                                           |
|   ------- before x2 seconds  ------------ |
|   <------- Send Vote -----------          |
|   --------------------------------------- |
|                                           |
|   ------- after x2 seconds  ------------- |
|   -------- Send Round Results ------->    |
|   --------------------------------------- |
|                                           |
|   ------- after x3 seconds -------------- |
|   -------- Either ----------------------- |
|   -------- Start again at --------------- |
|   ---- the first "Send Prompt" ---------- |
|   ------------ or ----------------------- |
|   --------   Send Game Results ---------> |



```

















