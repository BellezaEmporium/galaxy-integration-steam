import os
import sys

from . import messages
from .steam_types import ProtoUserInfo

__all__ = [
	"messages",
	"ProtoUserInfo",
]

base_dir = os.path.dirname(messages.__file__)
sys.path.append(base_dir)
