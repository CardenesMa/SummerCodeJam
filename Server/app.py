from typing import List
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse


app = FastAPI()

# keeping the html data seperate to de-clog this file
with open("index.html", "r") as f:
    html  = f.read()


class User:
   def __init__(self):
        self.userid=uuid.uuid4() # not sure how this is going to work with it all but we have it 
        self.socket: WebSocket
        self.sentence = None


class Lobby:
    def __init__(self):
        # self.active_connections: List[WebSocket] = []
        self.users = []
        self.lobbyID = uuid.uuid4()

    async def connect(self, user: User):
        await user.socket.accept()
        self.users.append(user)

    def disconnect(self, user:User):
        self.users.remove(user)

    async def send_personal_message(self, message: str, user:User):
        await user.socket.send_text(message)

    async def broadcast(self, message: str):
        for user in self.users:
            await user.socket.send_text(message)


manager = Lobby()


@app.get("/")
async def get():
    return HTMLResponse(html)




word = "Gregarious"

# server sends the word of the day to the lobby
async def send_word():  
    # add logic here so that it only sends a word once the game starts
    await manager.broadcast(f"The Word is... {word}")
    return True
    




@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket:WebSocket, client_id:int):
    # fill in user information based on websocket
    user = User()
    user.socket = websocket
    user.userid = client_id
    
    await manager.connect(user)
    try:
        
        word_sent = False
        while not word_sent: # block untill we have (2) players in the lobby to send the word
            word_sent = await send_word()
        
        # make the sentence time
        while not all([i.sentence for i in manager.users]): # block untill all the users send a sentence 
            data = await user.socket.receive_text()
            user.sentence = data
        print(data)
        await manager.broadcast(user.sentence) # send everones sentences 

        # ... now what? vote? refactor?
            
        ### from quickstart page
        # while True:
        #     data = await websocket.receive_text()
            
        #     await manager.send_personal_message(f"You wrote: {data}", websocket)
        #     await manager.broadcast(f"Client #{client_id} says: {data}")
        
    # acknowledge a user leaving the server
    except WebSocketDisconnect:
        manager.disconnect(user)
        await manager.broadcast(f"Client #{client_id} left the chat")


if __name__ == "__main__":
    import os
    os.system("uvicorn app:app --reload")