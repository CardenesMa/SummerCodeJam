from unittest import result
import uuid
import random

class Lobby:
	def __init__(self):
		# self.publicUUID=uuid.uuid4() # not sure how this is going to work with it all but we have it 
		self.users : dict = {} 
		self.lobby_id = random.randint(0,10000)
		self.privateUUID = uuid.uuid4()
  
	def __repr__(self) -> str:
		return f"Lobby#:{self.lobby_id} with {self.users}"
    
	@staticmethod
	def user_to_score_summary(userEntry):
		k, v = userEntry
		return {"score": v.score, "public_name": v.public_name, "rivate_id": k}


	def game_summary(self) -> list[dict]:
		return list(map(Lobby.user_to_score_summary, self.users.items()))
		
    
	def score_summary(self) -> dict:
		scores = {}
		for userID, user in self.users:
			scores[userID] = user.score
		return scores

	def make_sentenceResults_type(self):
		sentences=[]
		for (_, i) in self.users:
			temp_sent = {
				"private_id": i.privateUUID,
				"public_name" : i.publicName,
				"text" : i.sentence,
				"votes" : i.score//1000
			} 
			sentences.append(temp_sent)
		return sentences

	def round_summary(self):
		scores = [self.users[i].score for i in self.users]
		winning_score = max(scores)
		winning_user = self.users[scores.index(winning_score)]
		return {"winning_sent" : winning_user.sentence, "other_sents":self.make_sentenceResults_type()}
    
	def everyone_sent_message(self) -> bool:
		temp = True
		for (_ ,user) in self.users:
			if not user.sentence:
				temp = False
		return temp

