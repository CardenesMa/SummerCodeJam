from typing import List
import uuid
import Communications
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

# # keeping the html data seperate to de-clog this file
# with open("./User/Frontend/home.html", "r") as f:
#     html  = f.read()

# @app.get("/")
# async def get():
#     return HTMLResponse(html)

# @app.get("/main")
# async def getmain():
#     with open("./User/Frontend/main.html", "r") as f:
#         k = f.read()
#     return HTMLResponse(k)
    
# @app.get("/lobby")
# async def getlobby():
#     with open("./User/Frontend/lobby.html", "r")as f:
#         k = f.read()
#     return HTMLResponse(k)

# class User:
#    def __init__(self):
#         self.userid=uuid.uuid4() # not sure how this is going to work with it all but we have it 
#         self.socket: WebSocket
#         self.sentence = None


# class Lobby:
#     def __init__(self):
#         # self.active_connections: List[WebSocket] = []
#         self.users = []
#         self.lobbyID = uuid.uuid4()

#     async def connect(self, user: User):
#         await user.socket.accept()
#         self.users.append(user)

#     def disconnect(self, user:User):
#         self.users.remove(user)

#     async def send_personal_message(self, message: str, user:User):
#         await user.socket.send_text(message)

#     async def broadcast(self, message: str):
#         for user in self.users:
#             await user.socket.send_text(message)

#     async def broadcastAll(self):
#         for user in self.users:
#             await self.broadcast(user.sentence)
    
#     def clearAllSentences(self):
#         for user in self.users:
#             user.sentence = None

#     async def everyoneSentMessage(self):
#         flag = True
#         for user in self.users:
#             if user.sentence is None:
#                 flag = False
#             print(user.sentence)
#         return flag

# word = "Gregarious"
# manager = Lobby()
# # source ../myenv/bin/activate

# # server sends the word of the day to the lobby
# async def send_word():  
#     # add logic here so that it only sends a word once the game starts
#     await manager.broadcast(f"The Word is... {word}")
#     return True
    

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket:WebSocket, client_id:int):
    manager = Communications.ServerManager()
    
    server_working = True
    
    while server_working:
        # continuously listen to everything thats going on
        manager.listen()
        
        

    # fill in user information based on websocket
    # user = User()
    # user.socket = websocket
    # user.userid = client_id
    
    # await manager.connect(user)
    # await send_word()
    
    # try:
    #     while True:
    #         user.sentence = await user.socket.receive_text()
    #         print('This is', user.userid, '---', user.sentence)
    #         if await manager.everyoneSentMessage():
    #             await manager.broadcastAll()
    #             manager.clearAllSentences()
                
    # except WebSocketDisconnect:
    #     manager.disconnect(user)
    #     await manager.broadcast(f"Client #{client_id} left the chat")


import uvicorn
if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)