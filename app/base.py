""" A list of base classes
"""


from typing import Callable
import npyscreen
from openai import OpenAI


class ClientBase(OpenAI):
  """Base Class
  """
  max_yx:Callable[[], tuple[int, int]]


class MainFormBase(npyscreen.FormBaseNew):
  """Base Class
  """


class AppBase(npyscreen.NPSAppManaged):
  """Base Class
  """
  client:ClientBase
  form:MainFormBase
