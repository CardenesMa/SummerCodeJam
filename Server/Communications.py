from cgitb import handler
from dataclasses import dataclass
from distutils.log import debug, info, warn
import random
from textwrap import wrap
import typing
import uuid
from wsgiref.simple_server import server_version
from xmlrpc.client import Server
from fastapi import WebSocket, WebSocketDisconnect
import json
from Server.Lobby import Lobby
import asyncio
import Server.sentence as Sentence
from colorama import Fore, Back, Style
from .User import User


class PromptRepository(typing.Protocol):
	def get_random_prompt(self) -> str: ...

class FixedListPromptRepository(PromptRepository):
	def __init__(self):
		self.prompt_words = [
			"Racoon",
			"Clam",
			"Weezer",
			"Lancelot",
			"Abdullah",
			"P!ATD",
			"Taiwan",
			"Fidget Spinner",
			"Lamp"]
	def get_random_prompt(self) -> str:
		return random.choice(self.prompt_words)


#   listening for commands
# |  have the possible commands stored and accessible
# |  execute commands (RoundResult, UserInfo, UserJoined Lobby )




class ServerComms:

	# All the commands the server will send


	def __init__(self, websocket:WebSocket):
		self.websocket = websocket
		# this holds a pair "action" : [callback(),...]
		self.action_callbacks = {}
		self.user_id: str = ""

	@dataclass
	class SCPayload:
		sc: 'ServerComms'
		userId: str
		actionId: str
		payload: dict

	async def connect(self):
		await self.websocket.accept()

	async def disconnect(self):
		scp = ServerComms.SCPayload(self, self.user_id,"DISCONNECT",{})
		await self.handle_client_action("DISCONNECT", scp)
		pass

	async def receive(self, data):
		"""Used to listen to the websocket and execute commands as needed.
		"""
		try:
			# print(Fore.BLUE + "Incoming: ", data)
			# jsonify packet
			json_data = json.loads(data)
			scp = ServerComms.SCPayload(self,
				json_data["payload"]["private_id"],
				json_data["action"],
				json_data["payload"])
			await self.handle_client_action(scp.actionId, scp)
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

	async def handle_client_action(self, action:str, scp:SCPayload):
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
				r =  await callback(scp.userId, action, scp)
				returns.append(r)
			return returns

		else:
			print("Unhandled action recieved: ", action, scp.payload)



class ServerManager:
	"""ServerManager tells the ServerComms what to do. SM holds all the methods which are to be executed
	by an action.
	"""
	handlers={}

	def outer(handlers: dict):
		def register_handler(command_name: str) -> typing.Callable[
			['ServerManager', str, str, ServerComms.SCPayload], typing.Any]:
			def wrapper(h: typing.Callable[['ServerManager', str, str, ServerComms.SCPayload], typing.Any]):
				handlers[command_name] = h
				return h
			return wrapper
		return register_handler

	register_handler = outer(handlers)



	def __init__(self, pr: PromptRepository | None = None):
		"""This should be created under the @app.websocket("/ws/client_id") decorator
		"""
		# LobbyId -> Lobby
		self.lobbies: dict[str, Lobby] = {}

		# user.privateUUID -> User
		self.users: dict[str, User]  = {}

		# user.privateUUID -> ServerComms
		self.server_comms: dict[str, ServerComms] = {}

		self.awaiting_server_comms: dict[str, ServerComms] = {}

		self.pr = pr if (pr is not None) else FixedListPromptRepository()



	async def connect(self, server_comms: ServerComms):
		# self.server_comms.append(server_comms)
		await server_comms.connect()
		self.attach_client_handlers(server_comms)

	async def listen(self, data, server_comms):

		await server_comms.receive(data)

	async def disconnect(self, userId):
		# pop from the users
		user = self.users[userId]
		# pop the user before broadcasting to avoid errors
		lobby = self.lobbies.get(user.lobby_id)
		if lobby != None:
			lobby.users.pop(userId, None)

		# remove the comms object for this user to allow for gc
		self.server_comms.pop(userId, None)

		await self.send_server_action_to_lobby(
			userId,
			"USER_DISCONNECT",
			{"user": {"private_id" : userId, "public_name" : user.publicName}})
		user = self.users.pop(userId)


  # eventually this should remove the user from a lobby to keep people up to date


	def attach_client_handlers(self, server_comms: ServerComms):
		"""Assigns the action to the client. See ServerComms.register_callback()
		"""
		# Putting al the events and methods together to work
		# handler_action_pair = [(i,self.handlers_enum[j]) for j,i in enumerate(self.user_actions_enum)]
		# for pair in handler_action_pair:
		# 	server_comms.register_callback(
		# 		pair[0],
		# 		pair[1]
		# 	)
		for command_name, handler in ServerManager.handlers.items():
			server_comms.register_callback(
				command_name,
				handler.__get__(self, self.__class__) # bind self to handler
			)


	async def send(self, userId:str, action: str, payload: dict):
		# crate packet
		action_msg = json.dumps({'action':action, 'payload': payload})
		# send the packet
		await self.server_comms[userId].websocket.send_text(action_msg)
		# print(Fore.GREEN + f"Outgoing: {action}, payload : {payload} to {str(self.users[user].publicName)}")

	async def send_text(self, userId: str, text: str):
		await self.server_comms[userId].websocket.send_text(text)

	async def send_server_action_to_lobby(self, userId:str, action:str, payload:dict):
		# broadcast to lobby
		lobby_id = self.users[userId].lobby_id
		lobby = self.findLobby(lobby_id)
		if lobby is None:
			return warn(f"Could not find lobby with id {lobby_id}")

		msg = json.dumps({'action': action, 'payload': payload})
		debug(f"sending {msg} to lobby {lobby_id}")
		for uid in lobby.users:
			await self.send_text(uid, msg)


##### HELPER FUNCTIONS ########
	def findLobby(self, lobby_id):
		return self.lobbies.get(lobby_id)

###################################

	@register_handler("CREATE_LOBBY")
	async def create_lobby(self, userId: str, _, scp: ServerComms.SCPayload):
		lobby = Lobby()
		user = self.users[userId]

		lobby.users[userId] = user
		self.lobbies[lobby.lobby_id] = lobby

		user.publicName = scp.payload['public_name']
		user.lobby_id = lobby.lobby_id
		# do we also want to have the user join the lobby here?
		await self.send(
			userId,
			"ACK_JOIN",
			{"lobby_id" : lobby.lobby_id,
			'users':[{
				"public_name" : u.publicName,
				"private_id": u.privateUUID
				} for u in lobby.users.values()]
			})

	@register_handler("CONNECT")
	async def create_user(self, userId:str, _: str, scp: ServerComms.SCPayload):
		# payload {chosenID: "Geo", "privateUUID":1234-1234567-1234, "server_comm":ServerComms()}
		current_user = User()
		scp.sc.user_id = current_user.privateUUID
		self.server_comms[current_user.privateUUID] = scp.sc
		self.users[current_user.privateUUID] = current_user

		payload = {
			'private_id': current_user.privateUUID,
			'public_name': current_user.publicName,
				# we won't have the public name if has_record == false
		}

		await self.send(str(current_user.privateUUID), "USER_INFO", payload)
		print('User Created!')

	@register_handler("DISCONNECT")
	async def disconnect_user(self, userId: str, _, scp: ServerComms.SCPayload):
		await self.disconnect(scp.userId)
		pass

	@register_handler("JOIN_LOBBY")
	async def join_lobby(self, userId: str, _, scp: ServerComms.SCPayload):
		# find the correc lobby id to join

		current_lobby = self.findLobby(scp.payload['lobby_id'])
		if current_lobby is None:
			print("No lobby found... doing nothing")
			return

		user = self.users[userId]
		# add the user to the correct_lobby
		user.lobby_id = current_lobby.lobby_id
		user.publicName = scp.payload["public_name"]
		current_lobby.users[userId] = user

		await self.send(userId, "ACK_JOIN",
			{'lobby_id':
				scp.payload['lobby_id'],
				'users':[
					{"public_name" : u.publicName,
					"private_id":u.privateUUID
					} for u in current_lobby.users.values()]})
		await self.send_server_action_to_lobby(userId, "USER_CONNECT",
			{"user":{
				"private_id" : user.privateUUID,
				"public_name": user.publicName}})

	@register_handler("START_GAME")
	async def start_game(self, user, _:str, scp:ServerComms.SCPayload):
		# choose a random prompt word
		lobby_id = scp.payload["lobby_id"]
		target_lobby = self.findLobby(lobby_id)
		if target_lobby is None:
			return warn(f"No lobby with id {lobby_id} found.")

		if len(target_lobby.users) < 3:
			return warn("Not Enough Players to Start")

		word = self.pr.get_random_prompt()

		# fidn the lobby to start the game
		# broadcast the word to all the users
		await self.send_server_action_to_lobby(
			target_lobby.users[user].privateUUID,
			"SEND_PROMPT", {"prompt":word})

	@register_handler("SUBMIT_SENTENCE")
	async def send_sentence(self, user, _:str, scp:ServerComms.SCPayload):
		if random.random() > 0.75:
			sentence = Sentence.alter_sentence(scp.payload["sentence"])
		else:
			sentence = scp.payload["sentence"]
		self.users[user].sentence = sentence

		lobby_id = self.users[user].lobby_id

		lobby = self.findLobby(lobby_id)
		if lobby is None:
			return warn(f"could not find lobby id: {lobby_id}")

		if lobby.everyone_sent_message():
			await self.send_server_action_to_lobby(user, "SEND_SENT", {'sentences': lobby.game_summary()} )

	async def request_user_info(self, user, action:str, payload:dict):
		# TODO?
		await self.send(user, "USER_INFO", {"public_name":"DefaultName", "private_id" : self.users[user].publicUUID})

	@register_handler("SUBMIT_VOTE")
	async def vote_for_publicUUID(self, userId, action:str, scp:ServerComms.SCPayload):
		# add the score to our local user list
		current_lobby = self.findLobby(self.users[userId].lobby_id)
		if (current_lobby is None):
			return warn("Could not find lobby for voting user")

		userObj = self.users[scp.payload["target_id"]]
		userObj.score+=1000
		self.users[userId].voted = True
		# find the correct lobby to display the score
		# current_lobby.users[user].voted = True
		# self.users[user].voted = True

		# add th score to the user in the lobby
		# determine whether or not everyone voted
		if current_lobby.all_users_voted():
			await self.send_server_action_to_lobby(userId, "ROUND_RES", current_lobby.round_summary())
			await asyncio.sleep(5)
			await self.send_server_action_to_lobby(userId, "GAME_RES", {'scores': current_lobby.score_summary()})
			self.reset(userId, current_lobby)

	def reset(self, user:str, lobby:Lobby):
		self.lobbies.pop(lobby.lobby_id, None)
		for u in lobby.users.values():
			u.lobby_id = ""
			u.voted = False
			u.sentence = ""




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