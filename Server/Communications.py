
import uuid
from fastapi import WebSocket, WebSocketDisconnect
import json
from Lobby import Lobby

WSPORT = ":10000"
PROTOCOL = "ws://"

#   listening for commands
# |  have the possible commands stored and accessible
# |  execute commands (RoundResult, UserInfo, UserJoined Lobby )

class User:
   def __init__(self, chosenId: str = "DefultName"):
        # self.publicUUID=uuid.uuid4() # not sure how this is going to work with it all but we have it 
        self.privateUUID = uuid.uuid4()
        self.chosenId = chosenId
        self.socket: WebSocket
        self.sentence = None
        self.lobby_id: uuid
        

class ServerComms:
    
    # All the commands the server will send
    
    
    def __init__(self, hostname = "localhost", port = WSPORT):
        self.websocket = WebSocket(PROTOCOL + hostname + port)
        self.action_callbacks = {}
        
        self.connect()
        
    async def connect(self):
        await self.websocket.accept()
        
    async def recieve(self):
        # listen and feed data
        data = await self.websocket.receive_text()
        try:
            print(data)
            # jsonify packet
            json_data = json.loads(data)
            self.handle_client_action(json_data["action"], json_data)
        # handle appropriate exceptions
        except SyntaxError as e:
            print("Syntax Error : Invalid JSON recieved")
        except Exception as e:
            print("Something went wrong reading data. Traceback:" , e)

    # 
    def register_callback(self, action:str, action_consumer):
        if action in self.action_callbacks:
            self.action_callbacks[action].append(action_consumer)
        else:
            self.action_callbacks[action] = action_consumer
            
    def handle_client_action(self, action:str, action_object):
        if action in self.action_callbacks:
            for callback in self.action_callbacks[action]:
                callback(action, {{}, action_object["payload"]})
                
        else:
            print("Unhandled action recieved: ", action, action_object)

class ServerManager:
    
    def __init__(self, server_comms = ServerComms()):
        self.server_comms = server_comms
        self.attach_client_handlers()
        # self.users = []
        self.lobbies = []
        
        
        
        self.user_actions_enum = [
        "JoinLobby",
        "SendSentence",
        "RequestUserInfo",
        "StartGame",
        "VoteForPublicUUID",
        "CreateLobby",
        "CreateUser",
        "Authenticate"
    ]
        self.handlers_enum = [
            self.create_lobby,
            self.create_user,
            self.join_lobby,
            self.start_game,
            self.send_sentence,
            self.request_user_info,
            self.vote_for_publicUUID,
            self.authenticate        
        ]
        
    
    def attach_client_handlers(self):
        # Putting al the events and methods together to work
        handler_action_pair = [(i,j) 
                               for i in self.user_actions_enum
                               for j in self.handlers_enum]
        for pair in handler_action_pair:
            self.server_comms.register_callback(
                pair[0],
                # idk what `bind` is supposed to do here so I'm leaving it out. If something breaks here thats why
                pair[1]
            )
    
    
    async def send_server_action(self, user:User, action: str, payload: dict):
        action_msg = json.dumps({'action':action, 'payload': payload})
        user.socket.send_text(action_msg)
        print(f"sent message {action}:{payload} to {user.user_id}")
        
    async def send_server_action_to_lobby(self, user:User, action:str, payload:dict):
        # broadcast to lobby
        lobby_id = user.lobby_id
        lobby = self.findLobby(user.lobby_id)
        if lobby:
            for user in lobby.users:
                self.send_server_action(user,action,payload)
                print(f"boradcasted {action}, {payload} to lobby: {user.lobby_id}")
        else:
            print(f"no lobby: {user.lobby_id} found")
        
                
    def create_lobby(self,user, action, payload):
        lobby_id = uuid.uuid4()
        lobby = Lobby(lobby_id)
        self.lobbies.append(lobby)
        # do we also want to have the user join the lobby here?
        self.send_server_action(user, "CREATED_LOBBY", {})

        
        return lobby_id
    
    def findLobby(self, lobbyId):
        for lobby in self.lobbies:
            if lobby.lobby_id == lobbyId:
                return lobby
        return 'No Lobby Exists'
    
    def findUserInLobby(self,lobby,target_privateUUID):
        for user in lobby.users:
            if user.privateUUID == target_privateUUID: 
                return True 
        return False
        

    async def create_user(self, action: str, payload: dict):
        lobby_id = payload['lobby_id'] # there is no lobby_id in payload for create_use
        # payload {chosenID: "Geo", "privateUUID":1234-1234567-1234}
        # user.user_id = 
        currentLobby = self.findLobby(lobby_id)        

        if not self.findUserInLobby(currentLobby, payload['privateUUID']):
            user = User(payload['chosenId'])
            currentLobby.users.append(user)


    def join_lobby(self, lobby_id, user):
        lobby = self.findLobby(lobby_id) # what?
        if lobby:
            lobby.user_join(user)
        else:
            print(f"no lobby id {lobby_id}")
            # Send message to client that no lobby exsists
            self.server_send_action_to_user(user, "NO_LOBBY", {"msg":f"no lobby found with id {lobby_id}", "avalible_lobbies": self.lobbies})
        
        

    def start_game(self):
        pass

    def send_sentence(self):
        pass

    def request_user_info(self):
        pass

    def vote_for_publicUUID(self):
        pass

    def authenticate(self):
        pass
        





    
    




    

#   sending commands