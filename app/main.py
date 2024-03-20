#!/usr/bin/env python3

"""A ChatGPT Chat Application
"""

import curses
from typing import Callable
import npyscreen
from openai import OpenAI


class ConversationParent(OpenAI):
  """A parent class for conversations
  """
  def max_yx(self) -> tuple[int, int]:
    """Get the maximum y, x value for the chat view
    """
    return 20, 80


class Conversation:
  """A conversation object to hold messages and manage the conversation
  """
  name:str
  messages:list[dict[str,str]]
  client:ConversationParent

  def __init__(self, name:str, client:ConversationParent) -> None:
    self.name:str = name
    self.messages:list[dict[str,str]] = []
    self.client = client

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
      "user": " 💬 ❭❭ ",
      "system": "    🤖 ❬❬ "
    }
    values:list[str] = ['']
    max_y, max_x = self.client.max_yx()
    for message in self.messages:
      role = message["role"]
      content = message["content"]
      first = True
      prefix = prefixes[role]
      mx = max_x - len(prefix) - 5
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
          values.append(prefix + line)
          first = False
        else:
          values.append(" " * len(prefix + " ") + line)
      if role == "user":
        values.append("\n――――――")
      else:
        hr = "―" * (max_x - 3)
        values.append("\n" + hr)
    values.append('')
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


class Client(ConversationParent):
  """A client for the OpenAI ChatGPT API
  """
  model:str
  conversations:dict[str, Conversation]
  current_conversation:str
  max_yx:Callable[[], int]

  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.model = "gpt-3.5-turbo-0125"
    self.conversations:dict[str, Conversation] = {}
    self.current_conversation:str = "New Chat"
    self.conversations[self.current_conversation] = Conversation(self.current_conversation, self)
    self.conversations["chat2"] = Conversation("chat2", self)
    self.max_yx:Callable[[], int] = lambda: 20, 80

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
      self.conversations[conv_key] = Conversation(conv_key, self)
    conv = self.conversations[conv_key]
    messages = conv.messages
    messages.append({"role":"user", "content":prompt})
    completion = self.chat.completions.create(
      model=self.model,
      messages=messages
    )
    conv.messages.append({"role":"system", "content":completion.choices[0].message.content})


class MultiSelectHandled(npyscreen.MultiSelect):
  """A multi select widget with a custom handler
  """

  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.callbacks = []
    self.scroll_up_callback = []
    self.scroll_down_callback = []
    self.selected_indexes = []

  def when_check_value_changed(self) -> bool:
    """Handle the check value changed event

    Returns:
        bool: Always True
    """
    if self.cursor_line < 1:
      self.cursor_line = 1
      for callback in self.scroll_up_callback:
        callback()
    elif self.cursor_line > len(self.values) - 2:
      self.cursor_line = len(self.values) - 2
      for callback in self.scroll_down_callback:
        callback()
    if self.value != self.selected_indexes:
      self.selected_indexes = self.value
      selected_itms = [self.values[i] for i in self.value]
      for callback in self.callbacks:
        callback(selected_itms)
    return True


class ChatView(npyscreen.BoxTitle):
  """A view for displaying chat messages
  """
  _contained_widget = MultiSelectHandled

  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.callbacks = self.entry_widget.callbacks
    self.scroll_up_callback = self.entry_widget.scroll_up_callback
    self.scroll_down_callback = self.entry_widget.scroll_down_callback


class InputField(npyscreen.TitleText):
  """A field for entering chat messages
  """
  scroll_offset:int = 0

  def invoke(self) -> None:
    """Send the message to the chat model
    """
    self.scroll_offset = 0
    app:App = self.find_parent_app()
    prompt = self.value
    self.value = ""
    app.form.chat.values.append("⏳ GENERATING RESPONSE ...")
    app.form.chat.display()
    self.display()
    app.client.send(app.client.current_conversation, prompt)
    conv = app.client.conversations[app.client.current_conversation]
    chat_view = app.form.chat
    chat_view.values = conv.values(self.scroll_offset)
    chat_view.entry_widget.value = []
    chat_view.entry_widget.cursor_line = len(chat_view.values) - 1 - 1
    chat_view.display()
    self.value = ""
    self.display()


class SelectOneHandled(npyscreen.SelectOne):
  """A select one widget with a custom handler
  """

  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.callbacks = []
    self.selected_itm = None

  def when_check_value_changed(self) -> bool:
    """Handle the check value changed event

    Returns:
        bool: Always True
    """
    if len(self.value) > 0:
      index = self.value[0]
      selected_itm = self.values[index]
      if selected_itm != self.selected_itm:
        self.selected_itm = selected_itm
        for callback in self.callbacks:
          callback(selected_itm)
    return True


class SelectList(npyscreen.BoxTitle):
  """A list for selecting chat conversations
  """
  _contained_widget = SelectOneHandled

  def __init__(self, *args, **keywords) -> None:
    super().__init__(*args, **keywords)
    self.callbacks = self.entry_widget.callbacks


class MainForm(npyscreen.FormBaseNew):
  """The main form for the chat application
  """
  chat_list:SelectList
  chat:ChatView
  input:InputField
  editw:int

  def create(self) -> None:
    app:App = self.find_parent_app()
    y, x = tuple[int, int](self.useable_space())
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
    )
    self.chat_list.callbacks.append(self.chat_item_selected)
    # create chat view
    self.chat:ChatView = self.add(
    	ChatView,
    	name="Conversation",
    	relx=28,
    	rely=1,
    	max_width=x-30,
    	max_height=y-4,
    	values=[],
    )
    self.chat.scroll_up_callback.append(self.chat_scroll_up)
    self.chat.scroll_down_callback.append(self.chat_scroll_down)
    # create input
    self.input:InputField = self.add(
      InputField,
      name="Prompt:",
      relx=3,
      rely=y-3,
      use_two_lines=False,
    )
    self.input.add_handlers({
      curses.ascii.NL: self.input_enter,
    })
    self.editw = 0
    self.add_handlers({
      '^T': self.chat_copy,
      curses.ascii.ESC: self.quit_app,
      "^Q": self.quit_app,
    })

  def chat_scroll_up(self) -> None:
    """Scroll the chat view up
    """
    self.input.scroll_offset += 1
    app:App = self.find_parent_app()
    conv = app.client.conversations[app.client.current_conversation]
    self.chat.values = conv.values(self.input.scroll_offset)
    self.chat.entry_widget.value = []
    self.chat.display()

  def chat_scroll_down(self) -> None:
    """Scroll the chat view down
    """
    self.input.scroll_offset -= 1
    app:App = self.find_parent_app()
    conv = app.client.conversations[app.client.current_conversation]
    self.chat.values = conv.values(self.input.scroll_offset)
    self.chat.entry_widget.value = []
    self.chat.display()

  def chat_item_selected(self, item:str) -> bool:
    """Handle the chat item selected event

    Args:
        item (str): The selected chat item

    Returns:
        bool: Always True
    """
    self.chat.values.append("You selected " + item)
    self.chat.display()
    return True

  def quit_app(self, _:str) -> bool:
    """Quit the application

    Args:
        key (str): The key that was pressed

    Returns:
        bool: Always True
    """
    self.parentApp.switchForm(None)
    return True

  def chat_copy(self, _:str) -> bool:
    """Handle the chat copy event

    Args:
        key (str): The key that was pressed

    Returns:
        bool: Always True
    """
    self.chat.values.append("You pressed ^K")
    self.chat.display()
    return True

  def input_enter(self, _:str) -> bool:
    """Handle the input enter event

    Args:
        key (str): The key that was pressed

    Returns:
        bool: Always True
    """
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
    self.form = None

  def onStart(self) -> None:
    #npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
    self.form = self.addForm("MAIN", MainForm, name="Open AI Chat")

  def get_chat_max_yx(self) -> tuple[int, int]:
    """Get the maximum x value for the chat view

    Returns:
        int: The maximum x value
    """
    if self.form is None:
      return 20, 80
    x = self.form.chat.width
    y = self.form.chat.height
    return y, x


def main(*_:list[str]) -> None:
  """The main function

  Args:
      args (list[str]): The command line arguments
  """
  client = Client()
  app = App(client)
  client.max_yx = app.get_chat_max_yx
  app.run()


if __name__=="__main__":
  import sys
  if len(sys.argv) > 1:
    main(*(sys.argv[1:]))
  else:
    main(*[])
