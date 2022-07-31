
import uuid
from fastapi import WebSocket, WebSocketDisconnect
import json
from Lobby import Lobby


#   listening for commands
# |  have the possible commands stored and accessible
# |  execute commands (RoundResult, UserInfo, UserJoined Lobby )

class User:
	def __init__(self, publicName: str = "DefultName"):
		# self.publicUUID=uuid.uuid4() # not sure how this is going to work with it all but we have it 
		self.privateUUID = uuid.uuid4()
		self.publicName = publicName
		self.score = 0
		self.socket_id: int
		self.sentence = None
		self.lobby_id: uuid.UUID
		self.waiting_lobby = Lobby()
		

class ServerComms:
	
	# All the commands the server will send
	
	
	def __init__(self, websocket:WebSocket):
		self.websocket =websocket
		# this holds a pair "action" : [callback(),...]
		self.action_callbacks = {}
		self.lobbies = []

	
	
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
			await self.handle_client_action(json_data["payload"]["privateUUID"], json_data["action"], json_data)
		# handle appropriate exceptions
		except SyntaxError as e:
			print("Syntax Error : Invalid JSON recieved")
		
   
	
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
	
	def __init__(self, websocket, client_id : int):
		"""This should be created under the @app.websocket("/ws/client_id") decorator

		Args:
			websocket : (WebSocket): The webscocket which the communications will go through
			client_id (int): the identification of the websocket
		"""
		self.server_comms = ServerComms(websocket)
		self.lobbies = []
		# private UUID : User
		self.users = {}
		self.client_id = client_id
		self.waiting_lobby = Lobby()

		
		
		# a list of all the expected actions sent to the server
		self.user_actions_enum = [
		"JoinLobby",
		"SendSentence",
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
		handler_action_pair = [(i,self.handlers_enum[j]) for j,i in enumerate(self.user_actions_enum)]
		for pair in handler_action_pair:
			self.server_comms.register_callback(
				pair[0],
				# idk what `bind` is supposed to do here so I'm leaving it out. If something breaks here thats why
				pair[1]
			)
	
	
	async def send(self, user:str, action: str, payload: dict):
		# crate packet
		action_msg = json.dumps({'action':action, 'payload': payload})
		# send the packet 
		await self.server_comms.websocket.send_text(action_msg)
		print(f"sent message action : {action}, payload : {payload} to {self.users[user].publicName}")
		
  
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
		print("No Lobby Exists")
	
	def findUserInLobby(self,lobby,target_privateUUID):
		for user in lobby.users:
			if user.privateUUID == target_privateUUID: 
				return True 
		return False
###################################
				
	async def create_lobby(self,user, action, payload):
		lobby = Lobby()
		self.lobbies.append(lobby)
		# do we also want to have the user join the lobby here?
		await self.send(user, "CREATED_LOBBY", {"lobby_id" : lobby.lobby_id})

				
	async def create_user(self, user: User, action: str, payload: dict):
		# payload {chosenID: "Geo", "privateUUID":1234-1234567-1234}
		
		# current_user = User(publicName=payload['chosenID'])
		current_user = User()
		# current_user.privateUUID = payload['privateUUID']
		self.waiting_lobby.users[current_user.privateUUID] = current_user
  
		self.users[str(current_user.privateUUID)] = current_user

		payload = {
			'privateUUID': str(current_user.privateUUID),
			'publicName': current_user.publicName, 
		}

		await self.send(str(current_user.privateUUID), "USER_INFO", payload)
		print('User Created!')


	async def join_lobby(self, user, action, payload):
		# find the correc lobby id to join
		current_lobby = self.findLobby(payload['lobby_id'])
		# add the user to the correct_lobby
		current_lobby.users[user] = self.waiting_lobby.users[user]
		# delete from waiting lobby
		del self.waiting_lobby.users[user]


	async def start_game(self, user, action:str, payload:dict):
		pass

	async def send_sentence(self, user, action:str, payload:dict):
		pass

	async def request_user_info(self, user, action:str, payload:dict):
		await self.send(user, "USER_INFO", {"publicName":"DefaultName", "privateUUID" : self.users[user].publicUUID})

	async def vote_for_publicUUID(self, user, action:str, payload:dict):
		# there has to be a better way than n^2 time to do this. I'd reccomend using a hashmap or sending the user lobby
		# in the packet, but for now this is what we have.
		for lob in self.lobbies:
			for usr in lob.users:
				if usr.privateUUID == user:
					usr.score += 1
					break 
					

	async def authenticate(self, user, action:str, payload:dict):
		pass


# ToDo List:
# * finish the action methods