from protorpc import messages
from google.appengine.ext import ndb, db

class Game(ndb.Model) :
    name = ndb.StringProperty(required=True)
    playerTurn = ndb.IntegerProperty(default=0)
    game_over = ndb.BooleanProperty(default=False)

class GameForm(messages.Message) :
    name = messages.StringField(1, required=True)
    #users = messages.StringField(2, repeated=True)

class Profile(ndb.Model):
	"""Profile -- User profile object"""
	userId = ndb.StringProperty()
	displayName = ndb.StringProperty()
	mainEmail = ndb.StringProperty()


class ProfileMiniForm(messages.Message):
	"""ProfileMiniForm -- update Profile form message"""
	displayName = messages.StringField(1)


class ProfileForm(messages.Message):
	"""ProfileForm -- Profile outbound form message"""
	userId = messages.StringField(1)
	displayName = messages.StringField(2)
	mainEmail = messages.StringField(3)