"""Hello World API implemented using Google Cloud Endpoints.

Contains declarations of endpoint, endpoint methods,
as well as the ProtoRPC message class and container required
for endpoint method definition.
"""

from datetime import datetime

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import Game, GameForm, GameMiniForm
from settings import WEB_CLIENT_ID
from utils import getUserId

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID


class Hello(messages.Message):
  """String that stores a message."""
  greeting = messages.StringField(1)


@endpoints.api(name='battleshipendpoints', 
              version='v1',
              allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
              scopes=[EMAIL_SCOPE])
class BattleshipAPI(remote.Service):
  """Game API"""


 # - - - Game objects - - - - - - - - - - - - - - - - - - -
  def _createGameObject(self, request):
    """Create or update Game object, returning GameForm/request."""
    # preload necessary data items
    user = endpoints.get_current_user()
    if not user:
      raise endpoints.UnauthorizedException('Authorization required')
    user_id = getUserId(user)

    if not request.name:
      raise endpoints.BadRequestException("Game 'name' field required")

    # copy ConferenceForm/ProtoRPC Message into dict
    data = {field.name: getattr(request, field.name) for field in request.all_fields()}
    del data['websafeKey']
    del data['organizerDisplayName']

    # add default values for those missing (both data model & outbound Message)
    for df in DEFAULTS:
      if data[df] in (None, []):
        data[df] = DEFAULTS[df]
        setattr(request, df, DEFAULTS[df])

 
    # generate Profile Key based on user ID and Conference
    # ID based on Profile key get Conference key from ID
    p_key = ndb.Key(Profile, user_id)
    g_id = Game.allocate_ids(size=1, parent=g_key)[0]
    g_key = ndb.Key(Game, c_id, parent=g_key)
    data['key'] = g_key
    #data['organizerUserId'] = request.organizerUserId = user_id

    # create Conference, send email to organizer confirming
    # creation of Conference & return (modified) ConferenceForm
    Game(**data).put()
    
    return request

  @endpoints.method(GameMiniForm,GameForm,
                  name='create_game',
                  path= "game",
                  http_method="POST")
  def create_game(self, request) :
    """Create new conference."""
    #get the user ID first and make sure they're authorised
    user = endpoints.get_current_user()
    if not user:
      raise endpoints.UnauthorizedException('Authorization required')
    
    user_id = getUserId(user)

    #now create the game entity and insert it
    game = Game(owner=user_id, 
      player1=GameMiniForm.get('player1'), 
      player2=GameMiniForm.get('player2'),
      name=GameMiniForm.get('name'))

    playerTurn = 1
    #set the player turn randomly
    if bool(random.getrandbits(1)) :
      playerTurn = 1
    else :
      playerTurn = 2

    game.playerTurn = playerTurn

    game_key = game.put()
    url_key = game_key.urlsafe() 

    #return all of the game details, including a game key
    return GameForm(id=url_key, owner=user_id, 
      player1=game.player1, 
      player2=game.player2,
      name=game.name) 




APPLICATION = endpoints.api_server([BattleshipAPI])
