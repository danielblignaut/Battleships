"""Hello World API implemented using Google Cloud Endpoints.

Contains declarations of endpoint, endpoint methods,
as well as the ProtoRPC message class and container required
for endpoint method definition.
"""
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from models import Game, GameForm, ProfileForm, ProfileMiniForm
from settings import WEB_CLIENT_ID
import utils

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

  # - - - Profile objects - - - - - - - - - - - - - - - - - - -

  def _copyProfileToForm(self, prof):
    """Copy relevant fields from Profile to ProfileForm."""
    # copy relevant fields from Profile to ProfileForm
    pf = ProfileForm()
    for field in pf.all_fields():
      if hasattr(prof, field.name):
        # convert t-shirt string to Enum; just copy others
        setattr(pf, field.name, getattr(prof, field.name))
    pf.check_initialized()
    return pf


  def _getProfileFromUser(self):
    """Return user Profile from datastore, creating new one if non-existent."""
    user = endpoints.get_current_user()
    if not user:
      raise endpoints.UnauthorizedException('Authorization required')
    
    profile = None
    
    if not profile:
      profile = Profile(
        userId = None,
        key = None,
        displayName = user.nickname(), 
        mainEmail= user.email(),
      )

    return profile      # return Profile

  def _doProfile(self, save_request=None) :
    """Get user Profile and return to user, possibly updating it first."""
    # get user Profile
    prof = self._getProfileFromUser()

    # if saveProfile(), process user-modifyable fields
    if save_request:
      for field in ('displayName'):
        if hasattr(save_request, field):
          val = getattr(save_request, field)
          if val:
            setattr(prof, field, str(val))

    # return ProfileForm
    return self._copyProfileToForm(prof)


  @endpoints.method(message_types.VoidMessage, ProfileForm,
          path='profile', http_method='GET', name='getProfile')
  def getProfile(self, request):
    """Return user profile."""
    return self._doProfile()

  @endpoints.method(ProfileMiniForm, ProfileForm,
          path='profile', http_method='POST', name='saveProfile')
  def saveProfile(self, request):
    """Update & return user profile."""
    return self._doProfile(request)

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


  @endpoints.method(GameForm,GameForm,
                  name='create_game',
                  path= "game",
                  http_method="POST")
  def create_game(self, request) :
    """Create new conference."""
    return self._createGameObject(request)



APPLICATION = endpoints.api_server([BattleshipAPI])
