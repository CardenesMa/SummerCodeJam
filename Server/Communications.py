import random
import uuid
from fastapi import WebSocket, WebSocketDisconnect
import json
from Lobby import Lobby
import asyncio
import sentence as Sentence
from colorama import Fore, Back, Style



#   listening for commands
# |  have the possible commands stored and accessible
# |  execute commands (RoundResult, UserInfo, UserJoined Lobby )

class User:
	def __init__(self, publicName: str = "DefultName"):
		# self.publicUUID=uuid.uuid4() # not sure how this is going to work with it all but we have it 
		self.privateUUID = str(uuid.uuid4())
		self.publicName = publicName
		self.score = 0
		self.socket: WebSocket
		self.sentence = None
		self.lobby_id: str
		self.waiting_lobby = Lobby()
		self.voted = False
	
		

class ServerComms:
	
	# All the commands the server will send
	
	
	def __init__(self, websocket:WebSocket):
		self.websocket = websocket
		# this holds a pair "action" : [callback(),...]
		self.action_callbacks = {}
		self.lobbies = []

	
	
	async def connect(self):
		await self.websocket.accept()
		
	
	async def receive(self, data):
		"""Used to listen to the websocket and execute commands as needed.
		"""
		try:
			print(Fore.BLUE + "Incoming: ", data)
			# jsonify packet
			json_data = json.loads(data)
			await self.handle_client_action(json_data["payload"]["private_id"], json_data["action"], json_data)
		# handle appropriate exceptions
		except SyntaxError as e:
			print("Syntax Error : Invalid JSON recieved")
		# except Exception as e:
		# 	print(f"{e}")
   
	
	def register_callback(self, action:str, action_consumer):
		"""Makes the "action" : [callback(), ...] pair for self.action_callback

		Args:
			action (str): recieved packet action
			action_consumer (function): the function to execute given action
		"""
		if action in self.action_callbacks:
			self.action_callbacks[action].append(action_consumer)
		else:
			self.action_callbacks[action] = [action_consumer]
			
	async def handle_client_action(self,  user: str, action:str, action_object:dict):
		"""When called, it executes the function

		Args:
			user (uuid.UUID | str): publicUUID of the user to whom we send return packets
			action (str): the recievd action that prompts the method (mostly unused)
			action_object (function): the packet which prompted the method

		Returns:
			_type_: for debugging purposes, it returns the list of the outcomes of all the methods it calls
		"""
		returns = []
		action_object["payload"]["server_comm"] = self
		if action in self.action_callbacks:
			for callback in self.action_callbacks[action]:
				# execute that method and save it to the returns
				r =  await callback(user, action, action_object["payload"])
				returns.append(r)
			return returns
				
		else:
			print("Unhandled action recieved: ", action, action_object)



class ServerManager:
	"""ServerManager tells the ServerComms what to do. SM holds all the methods which are to be executed
	by an action. 
	"""
	
	def __init__(self):
		"""This should be created under the @app.websocket("/ws/client_id") decorator
		"""
		self.lobbies = []
		# private UUID : User
		self.users = {}
		self.waiting_lobby = Lobby()
		self.server_comms = []
		self.user_to_scs = {}
		self.prompt_words = ["Racoon", "Clam", "Weezer", "Lancelot", "Abdullah", "P!ATD", "Taiwan", "Fidget Spinner", "Lamp"]
		
		# a list of all the expected actions sent to the server
		self.user_actions_enum = [
		"JOIN_LOBBY",
		"SUBMIT_SENTENCE",
		"START_GAME",
		"SUBMIT_VOTE",
		"CREATE_LOBBY",
		"CONNECT"
	]
		# all the handlers, IN ORDER with the list above
		self.handlers_enum = [
			self.join_lobby,
			self.send_sentence,
			self.start_game,
			self.vote_for_publicUUID,
			self.create_lobby,
			self.create_user       
		]
		
	
	async def connect(self, server_comms: ServerComms, client_id):
		self.server_comms.append(server_comms)
		await server_comms.connect()
		self.attach_client_handlers(self.server_comms[-1])
  
	async def listen(self, data, server_comms):
		
		await server_comms.receive(data)
  
	async def disconnect(self, user):
		await self.send_server_action_to_lobby(user, "USER_DISCONNECT", {{"private_id" : user, "public_name" : self.users[user].publicName}})
		lobby = self.websockets[user].lobby_id
		del self.lobbies[self.lobbies.index(lobby)].users[user]
  # eventually this should remove the user from a lobby to keep people up to date


	def attach_client_handlers(self, server_comms: ServerComms):
		"""Assigns the action to the client. See ServerComms.register_callback()
		"""
		# Putting al the events and methods together to work
		handler_action_pair = [(i,self.handlers_enum[j]) for j,i in enumerate(self.user_actions_enum)]
		for pair in handler_action_pair:
			server_comms.register_callback(
				pair[0],
				pair[1]
			)
	
	
	async def send(self, user:str, action: str, payload: dict):
		# crate packet
		action_msg = json.dumps({'action':action, 'payload': payload})
		# send the packet 
		await self.user_to_scs[user].websocket.send_text(action_msg)
		print(Fore.GREEN + f"Outgoing: {action}, payload : {payload} to {str(self.users[user].publicName)}")
		
  
	async def send_server_action_to_lobby(self, user:str, action:str, payload:dict):
		# broadcast to lobby
		lobby = self.findLobby(self.users[user].lobby_id)
		for user in lobby.users:
			await self.send(user,action,payload)
			print(Fore.GREEN + f"Outgoing:  {action}, {payload} to lobby: {self.users[user].lobby_id}")

		
##### HELPER FUNCTIONS ########
	def findLobby(self, lobbyId):
		for lobby in self.lobbies:
			if lobby.lobby_id == int(lobbyId):
				return lobby
		print(f"No Lobby {lobbyId} Exists")
	
	def find(self,lobby,target_privateUUID):
		for user in lobby.users:
			if user.privateUUID == target_privateUUID: 
				return True 
		return False
###################################
				
	async def create_lobby(self, user, action, payload):
		lobby = Lobby()
		lobby.users[user] = self.users[user]
		self.lobbies.append(lobby)
		lobby.users[user].publicName = payload['public_name']
		self.users[user].lobby_id = lobby.lobby_id
		# do we also want to have the user join the lobby here?
		await self.send(user, "ACK_JOIN", {"lobby_id" : lobby.lobby_id, 'users':[{"public_name" : i.publicName, "private_id":i.privateUUID} for i in list(lobby.users.values())]})

	async def create_user(self, user:str, action: str, payload: dict):
		# payload {chosenID: "Geo", "privateUUID":1234-1234567-1234, "server_comm":ServerComms()}
		current_user = User()
		self.user_to_scs[current_user.privateUUID] = payload["server_comm"]
		# current_user.privateUUID = payload['privateUUID']
		self.waiting_lobby.users[str(current_user.privateUUID)] = current_user

		self.users[str(current_user.privateUUID)] = current_user

		payload = {
			'private_id': str(current_user.privateUUID),
				'public_name': current_user.publicName, 
				# we won't have the public name if has_record == false
		}

		await self.send(str(current_user.privateUUID), "USER_INFO", payload)
		print('User Created!')


	async def join_lobby(self, user, action, payload):
		# find the correc lobby id to join
  
		current_lobby = self.findLobby(payload['lobby_id'])
		if current_lobby is None:
			print("No lobby found... doing nothing")
			return 
		# add the user to the correct_lobby
		current_lobby.users[user] = self.waiting_lobby.users[user]
		current_lobby.users[user].lobby_id = payload['lobby_id']
		current_lobby.users[user].publicName = payload['public_name']
		# delete from waiting lobby
		del self.waiting_lobby.users[user]
		
		found_user = self.users[user]
		await self.send(user, "ACK_JOIN", {'lobby_id': payload['lobby_id'], 'users':[{"public_name" : i.publicName, "private_id":i.privateUUID} for i in list(current_lobby.users.values())]})
		await self.send_server_action_to_lobby(user, "USER_CONNECT", {"user":{"private_id" : found_user.privateUUID, "public_name": found_user.publicName}})


	async def start_game(self, user, action:str, payload:dict):
		# choose a random prompt word
		word = random.choice(self.prompt_words)
		lobby_id = payload["lobby_id"]
  
		# fidn the lobby to start the game
		target_lobby = self.findLobby(lobby_id)
		# broadcast the word to all the users
		await self.send_server_action_to_lobby(str(target_lobby.users[user].privateUUID), "SEND_PROMPT", {"prompt":word})
			
	async def send_sentence(self, user, action:str, payload:dict):
		if random.random() > 0.75:
			sentence = Sentence.alter_sentence(payload["sentence"])
		else:
			sentence = payload["sentence"]
		self.users[user].sentence = sentence
		lobby = self.findLobby(self.users[user].lobby_id)
		lobby.users[user].sentence = sentence
		
		if lobby.everyone_sent_message():
			await self.send_server_action_to_lobby(user, "SEND_SENT", {'sentences': lobby.game_summary()} )
		print('THIS is the', f'{user} sentence: ', self.users[user].sentence)
		

	async def request_user_info(self, user, action:str, payload:dict):
		await self.send(user, "USER_INFO", {"public_name":"DefaultName", "private_id" : self.users[user].publicUUID})

	async def vote_for_publicUUID(self, user, action:str, payload:dict):
		# add the score to our local user list
		self.users[user].score += 1000 
		# find the correct lobby to display the score
		current_lobby = self.findLobby(self.users[user].lobby_id)
		current_lobby.users[user].score += 1000
		current_lobby.users[user].voted = True
		self.users[user].voted = True

		# add th score to the user in the lobby
		# determine whether or not everyone voted
		if current_lobby.all_users_voted():
			await self.send_server_action_to_lobby(user, "ROUND_RES", current_lobby.round_summary())
			await asyncio.sleep(5)
			await self.send_server_action_to_lobby(user, "GAME_RES", {'scores': current_lobby.score_summary()})
			self.reset(user, current_lobby)

	def reset(self, user:str, lobby:Lobby):
		self.lobbies.remove(lobby)
		self.users[user].voted = False



# ToDo List:
# * finish the action methods
# * make the prompt sender

"""JS TESTER
var ws = new WebSocket("ws://127.0.0.1:8000/ws/2");
function run() {
    
    packet = {action:"CreateUser", payload:{privateUUID:"", has_record: 'False'}};
    ws.send(JSON.stringify(packet));
    id = "";
    lobbyid = "";
    ws.addEventListener("message", function (ev){
        ev = JSON.parse(ev.data);
        console.log(ev.action);
        switch(ev.action){
            case ("USER_INFO"):
                id = ev.payload.privateUUID;
                packet = {action:"CREATE_LOBBY",payload:{privateUUID:id}};
                ws.send(JSON.stringify(packet));
                break;
            case ("CREATE_LOBBY"):
                lobbyid = ev.payload.lobby_id;
                packet = {action:"JOIN_LOBBY", payload:{privateUUID:id, lobby_id:lobbyid}};
                ws.send(JSON.stringify(packet));
                break;
            case ("ACK_JOIN"):
                packet = {action:"START_GAME", payload:{privateUUID:id,lobby_id:lobbyid}};
                ws.send(JSON.stringify(packet));
                break;
            case ("SEND_PROMPT"):
                packet = {action:"SUBMIT_SENTENCE", payload:{privateUUID:id,sentence:" POKEMON, GOTTA CATCH EM ALL"}};
                ws.send(JSON.stringify(packet));
                break;

        }
    
    });
}
"""