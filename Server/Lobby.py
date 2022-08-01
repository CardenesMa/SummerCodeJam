from pickle import TRUE
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
		return {"score": v.score, "public_name": v.publicName, "private_id": k, "text":v.sentence}


	def game_summary(self) -> list[dict]:
		return list(map(Lobby.user_to_score_summary, self.users.items()))
		
    
	def score_summary(self) -> dict:
		scores = []
		for user in self.users:
			u = self.users[user]
			score_dict = {
				"score" : u.score,
				"private_id" : u.privateUUID,
				"public_name" : u.publicName
			}
			scores.append(score_dict)
		return scores

	def make_sentenceResults_type(self):
		sentences=[]
		for i in self.users:
			i = self.users[i]
			temp_sent = {
				"private_id": i.privateUUID,
				"public_name" : i.publicName,
				"text" : i.sentence,
				"votes" : i.score//1000
			} 
			sentences.append(temp_sent)
		return sentences

	def round_summary(self):
		# sort the users decreasingly by score
		scores = sorted(list(self.users),key=lambda x: self.users[x].score)
		print("List of Scores", scores)
		winning_user = self.users[scores[0]]
		return {"winning_sent" : winning_user.sentence, "other_sents":self.make_sentenceResults_type()}
    
	def everyone_sent_message(self) -> bool:
		temp = True
		for user in self.users:
			user = self.users[user]
			if not user.sentence:
				temp = False
		return temp

	def all_users_voted(self) -> bool:
		print("HERE")
		temp = True
		for user in self.users:
			user = self.users[user]
			if not user.voted:
				temp = False
		return temp

