import uuid
import random

class Lobby:
	def __init__(self):
		# self.publicUUID=uuid.uuid4() # not sure how this is going to work with it all but we have it 
		self.users = {}
		self.lobby_id = random.randint(0,10000)
		self.privateUUID = uuid.uuid4()
  
	def __repr__(self) -> str:
		return f"Lobby#:{self.lobby_id} with {self.users}"