#!/usr/bin/env python3

"""A ChatGPT Chat Application
"""

import curses
from xmlrpc.client import Boolean
import npyscreen # type: ignore
from openai import OpenAI


class Conversation:
  """A conversation object to hold messages and manage the conversation
  """
  name:str
  messages:list[dict[str,str]]
  max_x:int

  def __init__(self, name:str) -> None:
    self.name:str = name
    self.messages:list[dict[str,str]] = []
    self.max_x = -1

  def add(self, message:dict[str,str]) -> None:
    """Add a message to the conversation

    Args:
        message (dict[str,str]): A message object with a role and content
    """
    self.messages.append(message)

  def values(self) -> list[str]:
    """Return the messages in a format suitable for display

    Returns:
        list[str]: A list of strings to display
    """
    prefixes = {
      "user": " 💬 ❭❭ ",
      "system": "    🤖 ❬❬ "
    }
    values:list[str] = []
    for message in self.messages:
      role = message["role"]
      content = message["content"]
      lines = content.split("\n")
      first = True
      for line in lines:
        prefix = prefixes[role]
        if first:
          values.append(prefix + line)
          first = False
        else:
          values.append(" " + (" " * len(prefix)) + line)
      if role == "user":
        values.append("――――――")
      else:
        values.append("\n")
    return values


class Client(OpenAI):
  """A client for the OpenAI ChatGPT API
  """

  def __init__(self, *args, **kwargs) -> None: # type: ignore
    super().__init__(*args, **kwargs)
    self.model = "gpt-3.5-turbo-0125"
    self.conversations:dict[str, Conversation] = {}
    self.current_conversation:str = "New Chat"
    self.conversations[self.current_conversation] = Conversation(self.current_conversation)
    self.conversations["chat2"] = Conversation("chat2")

  def get_conversation(self) -> list[str]:
    """Get a list of conversation names
    """
    l:list[str] = []
    for [_, conv] in self.conversations.items():
      l.append(conv.name)
    return l

  def send(self, conv_key:str, prompt:str) -> None:
    """Send a message to the chat model

    Args:
        conv_key (str): The conversation key
        prompt (str): The message to send
    """
    prompt = prompt.strip()
    if len(prompt) == 0:
      return
    if conv_key not in self.conversations:
      self.conversations[conv_key] = Conversation(conv_key)
    conv = self.conversations[conv_key]
    messages = conv.messages
    messages.append({"role":"user", "content":prompt})
    completion = self.chat.completions.create(
      model=self.model,
      messages=messages # type: ignore
    )
    conv.messages.append({"role":"system", "content":completion.choices[0].message.content}) # type: ignore


class ChatView(npyscreen.BoxTitle):
  """A view for displaying chat messages
  """
  _contained_widget = npyscreen.Pager


class InputField(npyscreen.TitleText):
  """A field for entering chat messages
  """
  def invoke(self) -> None:
    """Send the message to the chat model
    """
    app:App = self.find_parent_app() # type: ignore
    app.client.send(app.client.current_conversation, self.value)
    conv = app.client.conversations[app.client.current_conversation]
    chat_view = app.form.chat
    chat_view.values = conv.values()
    chat_view.display()
    self.value = ""
    self.display()


class SelectList(npyscreen.BoxTitle):
  """A list for selecting chat conversations
  """

  def __init__(self, *args, **kwargs) -> None: # type: ignore
    super().__init__(*args, **kwargs) # type: ignore
    self.callbacks = []

  def when_check_value_changed(self) -> Boolean:
    selected_item:str = self.values[self.cursor_line] # type: ignore
    for callback in self.callbacks: # type: ignore
      callback(selected_item)
    return True


class MainForm(npyscreen.FormBaseNew):
  """The main form for the chat application
  """
  chat_list:SelectList
  chat:ChatView
  input:InputField
  editw:int

  def create(self) -> None:
    app:App = self.find_parent_app()
    y: int; x: int
    y, x = self.useable_space() # type: ignore
    # create chat list
    self.chat_list:SelectList = self.add(
      SelectList,
      name="Chats",
      custom_highlighting=True,
      values=app.client.get_conversation(),
      rely=1,
      relx=2,
      max_width=25,
      max_height=y-4,
    ) # type: ignore
    self.chat_list.callbacks.append(self.chat_item_selected)
    #                           self.chat_list.add_handlers({
    #                             curses.ascii.NL: lambda k: self.chat_list_enter(k),
    #                             '^T': lambda k: self.chat_list_enter(k),
    #                           })
    # create chat view
    self.chat:ChatView = self.add(
    	ChatView,
    	name="Conversation",
    	relx=28,
    	rely=1,
    	max_width=x-30,
    	max_height=y-4,
    	values=[],
    ) # type: ignore
    #                            self.chat.add_handlers({
    #                              '^K': lambda k: self.chat_copy(k),
    #                              curses.ascii.NL: lambda k: self.chat_list_enter(k),
    #                            })
    # create input
    self.input:InputField = self.add(
      InputField,
      name="Prompt:",
      relx=3,
      rely=y-3,
      use_two_lines=False,
    ) # type: ignore
    self.input.add_handlers({
      curses.ascii.NL: self.input_enter,
    })
    self.editw = 2
    self.add_handlers({
      #curses.ascii.UP: lambda k: self.chat.values.append("You pressed UP"),
      #curses.ascii.DOWN: lambda k: self.chat.values.append("You pressed DOWN"),
      '^T': self.chat_copy,
      curses.ascii.ESC: self.quit_app,
      "^Q": self.quit_app,
    })

  def chat_item_selected(self, item):
    self.chat.values.append("You selected " + item)
    self.chat.display()
    return True

  def quit_app(self, key):
    self.parentApp.switchForm(None)
    return True

  def chat_copy(self, key):
    self.chat.values.append("You pressed ^K")
    self.chat.display()
    return True

  def input_enter(self, key):
    self.input.invoke()
    return True


class App(npyscreen.NPSAppManaged):
  """The main application class
  """
  client:Client
  form:MainForm

  def __init__(self, client:Client) -> None:
    super().__init__()
    self.client = client

  def onStart(self) -> None:
    #npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
    self.form = self.addForm("MAIN", MainForm, name="Open AI Chat") # type: ignore


def main(args):
  client = Client()
  app = App(client)
  app.run()


if __name__=="__main__":
  import sys
  if len(sys.argv) > 1:
    main(sys.argv[1:])
  else:
    main([])
