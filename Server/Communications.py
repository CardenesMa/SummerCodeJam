
import uuid
from xmlrpc.client import Server
from fastapi import WebSocket, WebSocketDisconnect
import json
# from Lobby import Lobby


#   listening for commands
# |  have the possible commands stored and accessible
# |  execute commands (RoundResult, UserInfo, UserJoined Lobby )

class User:
	def __init__(self, chosenId: str = "DefultName"):
		# self.publicUUID=uuid.uuid4() # not sure how this is going to work with it all but we have it 
		self.privateUUID = uuid.uuid4()
		self.chosenId = chosenId
		self.socket_id: int
		self.sentence = None
		self.lobby_id: uuid
		

class ServerComms:
	
	# All the commands the server will send
	
	
	def __init__(self, websocket:WebSocket):
		self.websocket =websocket
		# this holds a pair "action" : [callback(),...]
		self.action_callbacks = {}

	
	
	async def connect(self):
		await self.websocket.accept()
		
	
	async def recieve(self):
		"""Used to listen to the websocket and execute commands as needed.
		"""
		data = await self.websocket.receive_text()
		try:
			print("Incoming Packet: ", data)
			# jsonify packet
			json_data = json.loads(data)
			self.handle_client_action(json_data["publicUUID"], json_data["action"], json_data)
		# handle appropriate exceptions
		except SyntaxError as e:
			print("Syntax Error : Invalid JSON recieved")
		except Exception as e:
			print("Something went wrong reading data. Here's whats wrong:" , e)
   
	
	def register_callback(self, action:str, action_consumer:function):
		"""Makes the "action" : [callback(), ...] pair for self.action_callback

		Args:
			action (str): recieved packet action
			action_consumer (function): the function to execute given action
		"""
		if action in self.action_callbacks:
			self.action_callbacks[action].append(action_consumer)
		else:
			self.action_callbacks[action] = [action_consumer]
			
	def handle_client_action(self,  user:uuid.UUID | str, action:str, action_object:dict):
		"""When called, it executes the function

		Args:
			user (uuid.UUID | str): publicUUID of the user to whom we send return packets
			action (str): the recievd action that prompts the method (mostly unused)
			action_object (function): the packet which prompted the method

		Returns:
			_type_: for debugging purposes, it returns the list of the outcomes of all the methods it calls
		"""
		returns = []
		if action in self.action_callbacks:
			for callback in self.action_callbacks[action]:
				# execute that method and save it to the returns
				r =  callback(user, action, {{}, action_object["payload"]})
				returns += r
			return returns
				
		else:
			print("Unhandled action recieved: ", action, action_object)



class ServerManager:
	"""ServerManager tells the ServerComms what to do. SM holds all the methods which are to be executed
	by an action. 
	"""
	
	def __init__(self, websocket, client_id : int):
		"""This should be created under the @app.websocket("/ws/client_id") decorator

		Args:
			websocket : (WebSocket): The webscocket which the communications will go through
			client_id (int): the identification of the websocket
		"""
		self.server_comms = ServerComms(websocket)
		self.lobbies = []
		self.client_id = client_id
		
		
		# a list of all the expected actions sent to the server
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
		# all the handlers, IN ORDER with the list above
		self.handlers_enum = [
			self.join_lobby,
			self.send_sentence,
			self.request_user_info,
			self.start_game,
			self.vote_for_publicUUID,
			self.create_lobby,
			self.create_user,
			self.authenticate        
		]
		self.attach_client_handlers()
		
	async def connect(self):
		return await self.server_comms.connect()
	async def listen(self):
		await self.server_comms.recieve()
	def disconnect(self):
		pass
		# eventually this should remove the user from a lobby to keep people up to date


	def attach_client_handlers(self):
		"""Assigns the action to the client. See ServerComms.register_callback()
		"""
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
	
	
	async def send(self, user:User, action: str, payload: dict):
		# crate packet
		action_msg = json.dumps({'action':action, 'payload': payload})
		# send the packet 
		user.socket.send_text(action_msg)
		print(f"sent message {action}:{payload} to {user.user_id}")
		
	async def send_server_action_to_lobby(self, user:User, action:str, payload:dict):
		# broadcast to lobby
		lobby_id = user.lobby_id
		lobby = self.findLobby(user.lobby_id)
		if lobby:
			for user in lobby.users:
				self.send(user,action,payload)
				print(f"boradcasted {action}, {payload} to lobby: {user.lobby_id}")
		else:
			print(f"no lobby: {user.lobby_id} found")
		
##### HELPER FUNCTIONS ########
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
###################################
				
	def create_lobby(self,user, action, payload):
		lobby_id = uuid.uuid4()
		lobby = Lobby(lobby_id)
		self.lobbies.append(lobby)
		# do we also want to have the user join the lobby here?
		self.send(user, "CREATED_LOBBY", {})

		
		return lobby_id

	async def create_user(self, user, action: str, payload: dict):
		lobby_id = payload['lobby_id'] # there is no lobby_id in payload for create_use
		# payload {chosenID: "Geo", "privateUUID":1234-1234567-1234}
		# user.user_id = 
		currentLobby = self.findLobby(lobby_id)        

		if not self.findUserInLobby(currentLobby, payload['privateUUID']):
			user = User(payload['chosenId'])
			currentLobby.users.append(user)


	def join_lobby(self, user, action, payload):
		lobby_id = payload["lobby_id"]
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


# ToDo List:
# * finish the action methods