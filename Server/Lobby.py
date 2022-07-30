import uuid

class Lobby:
    def __init__(self):
		# self.publicUUID=uuid.uuid4() # not sure how this is going to work with it all but we have it 
		self.privateUUID = uuid.uuid4()