
import json
from typing import List
import uuid
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

# keeping the html data seperate to de-clog this file
with open("./User/Frontend/home.html", "r") as f:
    html  = f.read()

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.get("/main")
async def getmain():
    with open("./User/Frontend/main.html", "r") as f:
        k = f.read()
    return HTMLResponse(k)
    
@app.get("/lobby")
async def getlobby():
    with open("./User/Frontend/lobby.html", "r")as f:
        k = f.read()
    return HTMLResponse(k)

@app.get("/game")
async def get_sentence_input():
    with open ("./User/Frontend/components/sentence-input.html", "r") as f:
        k = f.read()
    return HTMLResponse(k)

class User:
   def __init__(self):
        self.userid=uuid.uuid4() # not sure how this is going to work with it all but we have it 
        self.socket: WebSocket
        self.sentence = None
        self.ready = False


class Lobby:
    def __init__(self):
        # self.active_connections: List[WebSocket] = []
        self.users = []
        self.lobbyID = uuid.uuid4()

    async def connect(self, user: User):
        await user.socket.accept()
        self.users.append(user)

    async def on_user_join(self, user:User):
        
        await self.broadcast_event("MESSAGE", {"message":f'new user {user.userid} joined!'}) # change for argugments
        await self.send_personal_event(user, 'JOIN_LOBBY',  {'list_of_users': [user.userid for user in self.users]})
        await manager.broadcast_event('JOIN_LOBBY', {'new_users': user.userid})

    def disconnect(self, user:User):
        self.users.remove(user)
        print(user.userid, "Disconnected")

    async def send_personal_message(self, message: str, user:User):
        await user.socket.send_text(message)

    async def send_personal_event(self, user:User, action: str, payload: dict):
        event = {'action':action, 'payload':payload}
        await user.socket.send_text(json.dumps(event))

    async def broadcast_event(self, action, payload):
        event = {'action': action, 'payload': payload}
        for user in self.users:
            await user.socket.send_text(json.dumps(event))
    
    def clearAllSentences(self):
        for user in self.users:
            user.sentence = None

    async def everyoneSentMessage(self):
        flag = True
        for user in self.users:
            if user.sentence is None:
                flag = False
            print(user.sentence)
        return flag

    async def everyone_ready_up(self):
        for user in self.users:
            if not user.ready:
                return False
        return True

    async def ready_up_user(self, user: User):
        user.ready = True
        # check if all users are ready
        await self.broadcast_event("USER_READY_UP", {'user_id':user.user_id})
        if self.everyone_ready_up() and len(self.users) >= 2:
            await send_word()




manager = Lobby()
# source ../myenv/bin/activate

# server sends the word of the day to the lobby
async def send_word():  
    word = "Gregarious"
    # add logic here so that it only sends a word once the game starts
    await manager.broadcast_event('MESSAGE', {'message':f"The Word is... {word}"})
    '''
    await manage.broadcast_event('SEND_WORD', {'word': word}})
    '''
    return True
    
async def send_user_info(user):
    # create a custom uuid
    public_uuid = uuid.uuid4()
    private_uuid = uuid.uuid4()

    # I'm not sure what `chosenId` is on the sticky, so is "User1" for now
    chosen_id = "User1"
    
    packet = {
        "action" : "USER_INFO",
        "payload" : {
            "publicUUID" : str(public_uuid),
            "privateUUID" : str(private_uuid),
            "chosenId" : chosen_id
        }
    }
    await manager.send_personal_message(json.dumps(packet), user)
    # await manager.send_personal_event(user, 'USER_INFO', payload)
    return True

async def send_test_packet(user):
    packet = {
        "action" : "UserJoinedLobby",
        "payload" : {
            "userId" : "Nick",
            "publicUUID" : "123"
        }
    }
    
    packet2 = {
        "action" : "SendLobby",
        "payload" : {
            "lobbyId": "AKF-SKJ"
        }
    } 
    
    await user.socket.send_text(json.dumps(packet))
    await user.socket.send_text(json.dumps(packet2))
    

    

    


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket:WebSocket, client_id:int):
    # fill in user information based on websocket
    user = User()
    user.socket = websocket
    user.userid = client_id
    
    await manager.connect(user)

    # Player join lobby 
    await manager.on_user_join(user)
    
    # await send_test_packet(user) 
    # await send_test_packet(user) 
    
    try:
        # always be listening to the packet 
        while True:
            recieved_packet = await user.socket.receive_text()
            jsonified_packet = json.loads(recieved_packet)
            
            action = jsonified_packet["action"]
            payload = jsonified_packet["payload"]
            
            print('got from client: ', jsonified_packet)
            
            match action:
                case "CreateUser":
                    print('debug create user')
                    await send_user_info(user)
                    break 
                
                # idk how this will work yet
                case "CreateLobby": 
                    await manager.send_personal_message('make a lobby', user)
                    break
                
                case "ReadyUp":
                    await manager.ready_up_user()
                    break
                
                case "SendSentence":
                    pass

                
  
    except WebSocketDisconnect:
        manager.disconnect(user)
        await manager.broadcast_event('MESSAGE', {'message': f"Client #{client_id} left the chat"})


import uvicorn
if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)