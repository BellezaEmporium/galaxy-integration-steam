import asyncio
import base64
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class UserInfoCache:
    def __init__(self):
        self._steam_id: Optional[int] = None #unique id Steam assigns to the user
        self._account_username: Optional[str] = None #user name for the steam account.
        self._persona_name: Optional[str] = None #friendly name the user goes by in their display. It's what we use when saying "logged in" in the integration page.
        self._cell_id: Optional[int] = None #steam server cell id. This is used to determine which steam server to connect to. It is not a unique identifier for the user, but rather a location-based identifier for the server they are connected to. It can change if the user moves to a different location or if the server they are connected to changes.
        #Note: The tokens below are strings, but they are formatted as JSON Web Tokens (JWT). We can parse them to determine when the refresh token will expire.
        self._refresh_token : Optional[str] = None #persistent token. Used to log in, despite the fact that we should use an access token. weird quirk in how steam does things.
        self._access_token : Optional[str] = None #session login token. Largely useless. May be useful in future if steam fixes their login to use an access token instead of refresh token. 

        self._changed = False
        # legacy/auxiliary fields
        self._token: Optional[str] = None
        self._account_id: Optional[int] = None
        self._sentry: Optional[bytes] = None
        self._two_step: Optional[str] = None
        
        self.initialized = asyncio.Event()

    def _check_initialized(self):
        if self.is_initialized():
            logger.info("User info cache initialized")
            self.initialized.set()
            self._changed = True

    def is_initialized(self) -> bool:
        # Consider either a refresh token or a legacy token as valid initialization
        return all([self._steam_id is not None, self._account_username, self._persona_name, (self._refresh_token or self._token)])

    def to_dict(self):
        creds = {}
        if self.is_initialized():
            # encode a few values as base64 so they can safely store binary/utf8 data
            def b64(v: Optional[bytes]) -> Optional[str]:
                if v is None:
                    return None
                return base64.b64encode(v).decode('ascii')

            creds = {
                'steam_id': b64(str(self._steam_id).encode('utf-8')),
                'account_id': b64(str(self._account_id).encode('utf-8')) if getattr(self, '_account_id', None) is not None else None,
                'token': b64(self._token.encode('utf-8')) if self._token is not None else None,
                'refresh_token': self._refresh_token,
                'account_username': b64(self._account_username.encode('utf-8')) if self._account_username is not None else None,
                'persona_name': b64(self._persona_name.encode('utf-8')) if self._persona_name is not None else None,
                'sentry': b64(self._sentry) if getattr(self, '_sentry', None) is not None else None,
                'cell_id': self._cell_id,
            }
        return creds

    def from_dict(self, lookup: Dict[str, str]):
        for key, val in lookup.items():
            if val:
                logger.info(f"Loaded {key} from stored credentials")

        try:
            item = lookup.get('steam_id')
            if item is not None:
                try:
                    # steam_id stored as base64 of the decimal string
                    self._steam_id = int(base64.b64decode(item).decode('utf-8'))
                except Exception:
                    self._steam_id = int(item)

            item = lookup.get('account_id')
            if item is not None:
                try:
                    self._account_id = int(base64.b64decode(item).decode('utf-8'))
                except Exception:
                    self._account_id = int(item)

            item = lookup.get('account_username')
            if item is not None:
                try:
                    self._account_username = base64.b64decode(item).decode('utf-8')
                except Exception:
                    self._account_username = item

            item = lookup.get('persona_name')
            if item is not None:
                try:
                    self._persona_name = base64.b64decode(item).decode('utf-8')
                except Exception:
                    self._persona_name = item

            item = lookup.get('token') or lookup.get('access_token')
            if item is not None:
                try:
                    self._token = base64.b64decode(item).decode('utf-8')
                except Exception:
                    self._token = item

            item = lookup.get('refresh_token')
            if item is not None:
                self._refresh_token = item

            item = lookup.get('sentry')
            if item is not None:
                try:
                    self._sentry = base64.b64decode(item)
                except Exception:
                    self._sentry = item

            item = lookup.get('cell_id')
            if item is not None:
                self._cell_id = int(item)
        except (UnicodeDecodeError, ValueError, TypeError) as e:
            logger.warning(f"Failed to decode stored credentials (possibly corrupted or old format): {e}. Re-authentication will be required.")
            self.Clear()

    @property
    def changed(self):
        if self._changed:
            self._changed = False
            return True
        return False

    @property
    def account_id(self):
        return getattr(self, '_account_id', None)

    @account_id.setter
    def account_id(self, val):
        if getattr(self, '_account_id', None) != val and self.initialized.is_set():
            self._changed = True
        self._account_id = val
        if not self.initialized.is_set():
            self._check_initialized()

    @property
    def token(self):
        return getattr(self, '_token', None)

    @token.setter
    def token(self, val):
        if getattr(self, '_token', None) != val and self.initialized.is_set():
            self._changed = True
        self._token = val
        if not self.initialized.is_set():
            self._check_initialized()

    @property
    def sentry(self):
        return getattr(self, '_sentry', None)

    @sentry.setter
    def sentry(self, val):
        if getattr(self, '_sentry', None) != val and self.initialized.is_set():
            self._changed = True
        self._sentry = val
        if not self.initialized.is_set():
            self._check_initialized()

    @property
    def two_step(self):
        return getattr(self, '_two_step', None)

    @two_step.setter
    def two_step(self, val):
        if getattr(self, '_two_step', None) != val and self.initialized.is_set():
            self._changed = True
        self._two_step = val
        if not self.initialized.is_set():
            self._check_initialized()

    @property
    def steam_id(self):
        return self._steam_id

    @steam_id.setter
    def steam_id(self, val):
        if self._steam_id != val and self.initialized.is_set():
            self._changed = True
        self._steam_id = val
        if not self.initialized.is_set():
            self._check_initialized()

    @property
    def account_username(self):
        return self._account_username

    @account_username.setter
    def account_username(self, val):
        if self._account_username != val and self.initialized.is_set():
            self._changed = True
        self._account_username = val
        if not self.initialized.is_set():
            self._check_initialized()

    @property
    def persona_name(self):
        return self._persona_name

    @persona_name.setter
    def persona_name(self, val):
        if self._persona_name != val and self.initialized.is_set():
            self._changed = True
        self._persona_name = val
        if not self.initialized.is_set():
            self._check_initialized()

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, val):
        if self._access_token != val and self.initialized.is_set():
            self._changed = True
        self._access_token = val
        if not self.initialized.is_set():
            self._check_initialized()

    @property
    def refresh_token(self):
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, val):
        if self._refresh_token != val and self.initialized.is_set():
            self._changed = True
        self._refresh_token = val
        if not self.initialized.is_set():
            self._check_initialized()

    @property
    def cell_id(self):
        return self._cell_id
    
    @cell_id.setter
    def cell_id(self, val):
        if self._cell_id != val and self.initialized.is_set():
            self._changed = True
        self._cell_id = val
        if not self.initialized.is_set():
            self._check_initialized()

    def Clear(self):
        self._refresh_token = None
        self._steam_id = None 
        self._account_username = None 
        self._persona_name = None 
        self._access_token  = None
        self._cell_id = None
        # ensure initialized event reflects cleared state
        try:
            self.initialized.clear()
        except Exception:
            pass
