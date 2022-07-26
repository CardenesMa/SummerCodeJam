from typing import List
import uuid
import time
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

#number of players neeeded in a loby to start the gaem and send the word 
NUM_PLAYERS_TO_START = 2
TIME_PER_ROUND = 60

# keeping the html data seperate to de-clog this file
with open("./index.html", "r") as f:
	html  = f.read()

@app.get("/")
async def get():
	return HTMLResponse(html)

class User:
	def __init__(self):
		self.user_id=uuid.uuid4() # not sure how this is going to work with it all but we have it 
		self.socket: WebSocket
		self.sentence = None
		self.score = 0
		self.current_score = 0


class Lobby:
	def __init__(self):
		# self.active_connections: List[WebSocket] = []
		self.users = []
		self.lobbyID = uuid.uuid4()

	def get_user(self, user_id):
		for user in self.users:
			if user.user_id == user_id:
				return user
		

	def get_sentences(self):
		return {i.user_id:i.sentence for i in self.users}

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

	async def broadcast_all_sentences(self):
		for user in self.users:
			await self.broadcast(str(user.sentence) + ', ' + str(user.user_id))
	
	def clear_all_sentences(self):
		for user in self.users:
			user.sentence = None

	def everyone_sent_message(self):
		flag = True
		for user in self.users:
			if user.sentence is None:
				flag = False
			print(user.sentence)
		return flag

	async def send_personal_event(self, user:User, action: str, payload: dict):
		'''
		{
		'action': SEND_WORD
		'payload'
			{'word': Poop}
		}
		'''
		msg = json.dumps({'action':action, 'payload':payload})
		await user.socket.send_json(msg)

	"""
	async def send_sentences(self, user:User):
		action = 'SEND_ALL_SENTENCES'
		payload = {
			"sentence_objects": [
				{ 
					'user_id': user.user_id , 
					'sentence': user.sentence
					
				} for user in self.users]
		}
		for user in self.users:
			self.send_personal_event(user, action, payload)
			
	"""

word = "Gregarious"
manager = Lobby()
# source ../myenv/bin/activate

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
	user.user_id = client_id
	
	await manager.connect(user)
	await manager.broadcast(f"client {client_id} connected!")


	if len(manager.users) == NUM_PLAYERS_TO_START: 
		await send_word()
		manager.clear_all_sentences()
		await manager.broadcast(f'time starts now {time.time()} You have 10 seconds to write a sentence')
	
	try:
		# Need to await for a ready before the next event goes through!! 
		while True:
			# await before next round? 
			try:
				user.sentence = await asyncio.wait_for(user.socket.receive_text(), timeout= 10.0)
			except asyncio.TimeoutError:
				user.sentence = ''
				await manager.send_personal_message(f'Sorry you took too long!!!', user)	
			if manager.everyone_sent_message():
				# sending sentences back for voting 
				await manager.broadcast_all_sentences()
				
				# wait for each clients voting responces
				# vote is going to be the senteces/user_id and a value score attached to each
				# {user_id: value, user_id2: value2}
		
				# vote = await user.socket.receive_text()
				# for user_id, rank in vote.items():
				# 	found_user = manager.get_user('user_id')
				# 	found_user.current_score += rank
				

				# send the results 
				# broadcast all scores and sentences
				# for user in users: 
				# user.socket.send_json()
				



				all_sentences = manager.get_sentences()

				manager.clear_all_sentences()
				


			
					
	except WebSocketDisconnect:
		manager.disconnect(user)
		await manager.broadcast(f"Client #{client_id} left the chat")


if __name__ == "__main__":
	import os
	os.system("uvicorn app:app --reload")