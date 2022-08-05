import functools
import uuid
import random

from .User import User

class Lobby:
	def __init__(self):
		# self.publicUUID=uuid.uuid4() # not sure how this is going to work with it all but we have it
		self.users : dict[str, User] = {}
		self.lobby_id = f"{random.randint(0,100_000):06}" # different method forthcoming
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

	def user_to_sentence_result(self, userId):
		user = self.users[userId]
		return {
			"private_id": user.privateUUID,
			"public_name": user.publicName,
			"text": user.sentence,
			"votes": user.score//1000,
		}


	def round_summary(self):
		# sort the users decreasingly by score
		# scores = sorted(list(self.users),key=lambda x: self.users[x].score)
		maxId = max(self.users.values(), key=lambda u: u.score).privateUUID
		# print("List of Scores", scores)
		# winning_user = self.users[scores[0]]
		return {
			"winning_sent" : self.user_to_sentence_result(maxId),
			"other_sents": [self.user_to_sentence_result(k) for k in self.users.keys() if k != maxId]
			}

	def everyone_sent_message(self) -> bool:
		return all(u.sentence for u in self.users.values())


	def all_users_voted(self) -> bool:
		return all(u.voted for u in self.users.values())

