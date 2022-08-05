import uuid

class User:
	def __init__(self, publicName: str = "DefultName"):
		# self.publicUUID=uuid.uuid4() # not sure how this is going to work with it all but we have it
		self.privateUUID = str(uuid.uuid4())
		self.publicName = publicName
		self.score = 0
		self.sentence: str | None = None
		self.lobby_id: str
		self.voted = False
