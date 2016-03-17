from protorpc import messages
from google.appengine.ext import ndb, db

class Game(ndb.Model) :
    
    playerTurn = ndb.IntegerProperty(default=1)
    gameOver = ndb.BooleanProperty(default=False)

    name = ndb.StringProperty(required=True)
    owner = db.StringProperty(required=True)
    player1 = ndb.StringProperty(required= True)
    player2 = ndb.StringProperty(required= True)


class GameMiniForm(messages.Message) :
    name = messages.StringField(1, required=True)
    player1 = messages.StringField(2, required=True)
    player2 = messages.StringField(3, required=True)

class GameForm(messages.Message) :
    name = messages.StringField(1, required=True)
    owner = messages.StringField(2, required=True)
    playerTurn = messages.IntegerField(3, required=True)
    gameOver = messages.BooleanField(4, required= True)
    player1 = messages.StringField(5, required=True)
    player2 = messages.StringField(6, required=True)
    id = messages.StringField(7, required=True)