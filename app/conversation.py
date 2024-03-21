"""A module to manage conversations
"""


import os
import json
from constants import CONVERSATIONS_FOLDER_PATH, FILE_EXTENSION
import functions
import base
from labels import Lang


class Conversation:
  """A conversation object to hold messages and manage the conversation
  """
  name:str
  messages:list[dict[str,str]]
  client:base.ClientBase
  path:str

  def __init__(self, name:str, client:base.ClientBase) -> None:
    self.name:str = name
    self.messages:list[dict[str,str]] = []
    self.client = client

  def save(self, path="") -> None:
    """Save the conversation to a file
    """
    if len(path) <= 0:
      self.path = functions.get_home_folder() + CONVERSATIONS_FOLDER_PATH + self.name + FILE_EXTENSION
    else:
      self.path = path
    json_str = json.dumps(self.messages)
    with open(self.path, "w+", encoding='utf-8') as f:
      f.write(json_str)

  def load(self, path="") -> None:
    """Load the conversation from a file
    """
    if len(path) <= 0:
      self.path = functions.get_home_folder() + CONVERSATIONS_FOLDER_PATH + self.name + FILE_EXTENSION
    else:
      self.path = path
    try:
      with open(self.path, "r", encoding='utf-8') as f:
        json_str = f.read()
        self.messages = json.loads(json_str)
    except FileNotFoundError:
      pass

  def delete(self) -> None:
    """Delete the conversation file
    """
    if len(self.path) <= 0:
      self.path = functions.get_home_folder() + CONVERSATIONS_FOLDER_PATH + self.name + FILE_EXTENSION
    if os.path.exists(self.path):
      os.remove(self.path)

  def add(self, message:dict[str,str]) -> None:
    """Add a message to the conversation

    Args:
        message (dict[str,str]): A message object with a role and content
    """
    self.messages.append(message)

  def values(self, scroll_offset:int) -> list[str]:
    """Return the messages in a format suitable for display

    Returns:
        list[str]: A list of strings to display
    """
    prefixes = {
      "user": Lang.cur.conversation_user_prefix,
      "system": Lang.cur.conversation_system_prefix
    }
    values:list[str] = ['']
    max_y, max_x = self.client.max_yx()
    if len(self.messages) <= 0:
      values.append(Lang.cur.conversation_new_conversation_line1)
      values.append(Lang.cur.conversation_new_conversation_line2)
    for message in self.messages:
      role = message["role"]
      content = message["content"]
      first = True
      prefix = prefixes[role]
      mx = max_x - len(prefix) - 12
      lines = []
      for content_line in content.split("\n"):
        words = content_line.split(" ")
        line = ""
        for word in words:
          if len(line) + len(word) + 1 < mx:
            line += word + " "
          else:
            lines.append(line)
            line = word + " "
        if len(line) > 0:
          lines.append(line)
      for line in lines:
        if first:
          values.append(prefix + line + " ")
          first = False
        else:
          values.append(" " * len(prefix) + line + " ")
      if role == "user":
        values.append("\n―――――― ")
      else:
        hr = "―" * (mx - 3)
        values.append("\n" + hr + " ")
    values.append(' ')
    my = max_y - 4
    if len(values) < my:
      return values
    else:
      start = len(values) - my - scroll_offset
      if start < 0:
        start = 0
      if start + my > len(values):
        start = len(values) - my
      end = start + my
      return values[start:end]
