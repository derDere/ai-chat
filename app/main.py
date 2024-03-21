#!/usr/bin/env python3

"""A ChatGPT Chat Application
"""

import curses
import json
import os
from typing import Callable
import npyscreen
from openai import OpenAI


def get_home_folder() -> str:
  """Get the home folder

  Returns:
      str: The home folder
  """
  return os.path.expanduser("~")


def create_folder(path:str) -> None:
  """Get or create a folder

  Args:
      path (str): The path to the folder
  """
  if not os.path.exists(path):
    os.makedirs(path)


def list_conversation_files() -> dict[str,str]:
  """List the conversation files

  Returns:
      list[str]: A list of conversation file names
  """
  path = get_home_folder() + "/.openai-chat/conversations/"
  create_folder(path)
  conversations = {}
  files = os.listdir(path)
  for file in files:
    if file.endswith(".json"):
      key = file.replace(".json", "")
      file_path = path + file
      conversations[key] = file_path
  return conversations


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
  path:str

  def __init__(self, name:str, client:ConversationParent) -> None:
    self.name:str = name
    self.messages:list[dict[str,str]] = []
    self.client = client

  def save(self, path="") -> None:
    """Save the conversation to a file
    """
    if len(path) <= 0:
      self.path = get_home_folder() + "/.openai-chat/conversations/" + self.name + ".json"
    else:
      self.path = path
    json_str = json.dumps(self.messages)
    with open(self.path, "w+", encoding='utf-8') as f:
      f.write(json_str)

  def load(self, path="") -> None:
    """Load the conversation from a file
    """
    if len(path) <= 0:
      self.path = get_home_folder() + "/.openai-chat/conversations/" + self.name + ".json"
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
      self.path = get_home_folder() + "/.openai-chat/conversations/" + self.name + ".json"
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
      "user": " 💬 ❭❭ ",
      "system": "    🤖 ❬❬ "
    }
    values:list[str] = ['']
    max_y, max_x = self.client.max_yx()
    if len(self.messages) <= 0:
      values.append("    NEW CONVERSATION ")
      values.append("    > waiting for prompt ... ")
    for message in self.messages:
      role = message["role"]
      content = message["content"]
      first = True
      prefix = prefixes[role]
      mx = max_x - len(prefix) - 5 - 1
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
          values.append(" " * len(prefix + " ") + line + " ")
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
    self.current_conversation:str = None
    #self.conversations[self.current_conversation] = Conversation(self.current_conversation, self)
    #self.conversations["chat2"] = Conversation("chat2", self)
    self.max_yx:Callable[[], int] = lambda: 20, 80
    conversation_list = list_conversation_files()
    for [key, path] in conversation_list.items():
      conv = Conversation(key, self)
      conv.load(path)
      self.conversations[key] = conv
    if len(self.conversations) > 0:
      self.current_conversation = list(self.conversations.keys())[0]


  def get_conversation(self) -> list[str]:
    """Get a list of conversation names
    """
    l:list[str] = []
    if self.conversations is None:
      self.conversations = {}
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
    conv:Conversation
    if conv_key is None:
      conv = Conversation("<<new>>", self)
    elif conv_key not in self.conversations:
      self.conversations[conv_key] = Conversation(conv_key, self)
      conv = self.conversations[conv_key]
    else:
      conv = self.conversations[conv_key]
    messages = conv.messages
    messages.append({"role": "user", "content": prompt})
    completion = self.chat.completions.create(
      model=self.model,
      messages=messages
    )
    conv.messages.append({"role":"system", "content":completion.choices[0].message.content})
    if conv_key is None:
      # get conv name
      name_completion = self.chat.completions.create(
        model=self.model,
        messages= messages + [{
          "role": "user",
          "content": "Generate a name for this conversation. " +
                     "Max of 25 characters and UpperCamelCase! " +
                     "Your answer should only contain this name! " +
                     "No formatting not special characters!"
        }],
      )
      conv_key = name_completion.choices[0].message.content
      conv.name = conv_key
      self.conversations[conv_key] = conv
    conv.save()
    return conv_key


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
    app.form.chat.clear()
    app.form.chat.display()
    self.display()
    new_conf_key = app.client.send(app.client.current_conversation, prompt)
    if app.client.current_conversation != new_conf_key:
      app.client.current_conversation = new_conf_key
      app.form.chat_list.values = app.client.get_conversation()
      app.form.chat_list.entry_widget.value = [list(app.client.conversations.keys()).index(app.client.current_conversation)]
      app.form.chat_list.display()
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
  delete_chat_mode:bool
  rename_chat_mode:bool
  created:bool

  def create(self) -> None:
    side_col_width = 30
    self.delete_chat_mode = False
    self.rename_chat_mode = False
    self.created = False
    app:App = self.find_parent_app()
    y, x = tuple[int, int](self.useable_space())
    # create input
    self.input:InputField = self.add(
      InputField,
      name="Prompt:        ",
      relx=side_col_width + 4,
      rely=y-3,
      use_two_lines=False,
    )
    # create chat view
    self.chat:ChatView = self.add(
    	ChatView,
    	name="Conversation",
    	relx=side_col_width + 3,
    	rely=1,
    	max_width=x-side_col_width-5,
    	max_height=y-4,
    )
    # create chat list
    self.chat_list:SelectList = self.add(
      SelectList,
      name="Chats",
      custom_highlighting=True,
      values=app.client.get_conversation(),
      rely=1,
      relx=2,
      max_width=side_col_width,
      max_height=y-4-3,
    )
    # create new chat button
    self.new_chat_btn = self.add(
      npyscreen.ButtonPress,
      name="[   + New Chat   (^N) ]",
      relx=1,
      rely=y-3-3,
      max_width=side_col_width,
      when_pressed_function=self.new_chat,
      color="GOOD",
    )
    # create rename chat button
    self.rename_chat_btn = self.add(
      npyscreen.ButtonPress,
      name="[   Rename Chat  (^R) ]",
      relx=1,
      rely=y-3-2,
      max_width=side_col_width,
      when_pressed_function=self.rename_chat,
    )
    # create delete chat button
    self.delete_chat_btn = self.add(
      npyscreen.ButtonPress,
      name="[   Delete Chat  (^D) ]",
      relx=1,
      rely=y-3-1,
      max_width=side_col_width,
      when_pressed_function=self.delete_chat,
    )
    # create quit button
    self.quit_btn = self.add(
      npyscreen.ButtonPress,
      name="[      Quit      (^Q) ]",
      relx=1,
      rely=y-3,
      max_width=side_col_width,
      when_pressed_function=self.quit_app,
      color="DANGER",
    )
    # add key handlers
    self.chat.scroll_up_callback.append(self.chat_scroll_up)
    self.chat.scroll_down_callback.append(self.chat_scroll_down)
    app.client.max_yx = lambda: tuple([y-4, x-side_col_width-5])
    self.input.add_handlers({
      curses.ascii.NL: self.input_enter,
    })
    if app.client.current_conversation is not None:
      self.chat_list.entry_widget.value = [list(app.client.conversations.keys()).index(app.client.current_conversation)]
      self.chat.values = app.client.conversations[app.client.current_conversation].values(0)
    self.chat_list.callbacks.append(self.chat_item_selected)
    # check if conversation list is empty
    if len(app.client.conversations) <= 0:
      self.new_chat()
    # add key handlers
    self.add_handlers({
      #'^T': self.chat_copy,
      "^N": self.new_chat,
      "^R": self.rename_chat,
      "^D": self.delete_chat,
      curses.ascii.ESC: self.quit_app,
      "^Q": self.quit_app,
    })
    # focus input widget
    self.editw = 0
    self.created = True

  def new_chat(self, _:str=None) -> bool:
    """Create a new chat
    """
    app = self.find_parent_app()
    app.client.current_conversation = None
    self.input.value = ""
    self.input.label_widget.value = "New Chat Name: "
    self.input.display()
    newcon = Conversation("new", self.find_parent_app().client)
    self.chat.values = newcon.values(0)
    self.chat.clear()
    self.chat.display()
    self.editw = 0
    if self.created:
      self.input.edit()

  def rename_chat(self, _:str=None) -> bool:
    """Rename the chat
    """
    self.rename_chat_mode = True
    self.input.label_widget.value = "Rename Chat:   "
    self.input.value = self.find_parent_app().client.current_conversation
    self.input.display()
    if self.created:
      self.input.edit()

  def delete_chat(self, _:str=None) -> bool:
    """Delete the chat
    """
    self.delete_chat_mode = True
    self.input.label_widget.value = "Delete Chat:   "
    self.input.value = "type in DELETE to confirm"
    self.input.display()
    self.editw = 0
    if self.created:
      self.input.edit()

  def chat_scroll_up(self) -> None:
    """Scroll the chat view up
    """
    self.input.scroll_offset += 1
    app:App = self.find_parent_app()
    if app.client.current_conversation is None:
      return
    conv = app.client.conversations[app.client.current_conversation]
    self.chat.values = conv.values(self.input.scroll_offset)
    self.chat.entry_widget.value = []
    self.chat.clear()
    self.chat.display()

  def chat_scroll_down(self) -> None:
    """Scroll the chat view down
    """
    self.input.scroll_offset -= 1
    app:App = self.find_parent_app()
    if app.client.current_conversation is None:
      return
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
    app:App = self.find_parent_app()
    app.client.current_conversation = item
    self.input.scroll_offset = 0
    conv = app.client.conversations[item]
    self.chat.values = conv.values(0)
    self.chat.entry_widget.value = []
    self.chat.clear()
    self.chat.display()
    self.chat.cursol_line = len(self.chat.values) - 1
    return True

  def quit_app(self, _:str=None) -> bool:
    """Quit the application

    Args:
        key (str): The key that was pressed

    Returns:
        bool: Always True
    """
    self.parentApp.switchForm(None)
    return True

  def chat_copy(self, _:str=None) -> bool:
    """Handle the chat copy event

    Args:
        key (str): The key that was pressed

    Returns:
        bool: Always True
    """
    self.chat.values.append("You pressed ^K")
    self.chat.clear()
    self.chat.display()
    return True

  def input_enter(self, _:str=None) -> bool:
    """Handle the input enter event

    Args:
        key (str): The key that was pressed

    Returns:
        bool: Always True
    """
    if self.rename_chat_mode:
      app = self.find_parent_app()
      if app.client.current_conversation is not None:
        if app.client.current_conversation in app.client.conversations:
          if app.client.current_conversation != self.input.value:
            conv = app.client.conversations[app.client.current_conversation]
            app.client.conversations.pop(app.client.current_conversation)
            conv.delete()
            conv.name = self.input.value
            app.client.conversations[conv.name] = conv
            conv.save()
            app.client.current_conversation = conv.name
            self.chat_list.values = app.client.get_conversation()
            self.chat_list.entry_widget.value = [list(app.client.conversations.keys()).index(app.client.current_conversation)]
            self.chat_list.display()
      self.rename_chat_mode = False

    elif self.delete_chat_mode:
      app = self.find_parent_app()
      if app.client.current_conversation is not None:
        if app.client.current_conversation in app.client.conversations:
          if self.input.value == "DELETE":
            conv = app.client.conversations[app.client.current_conversation]
            app.client.conversations.pop(app.client.current_conversation)
            conv.delete()
            if len(app.client.conversations) > 0:
              app.client.current_conversation = list(app.client.conversations.keys())[0]
              self.chat_list.values = app.client.get_conversation()
              self.chat_list.entry_widget.value = [list(app.client.conversations.keys()).index(app.client.current_conversation)]
              self.chat_list.display()
              self.chat.values = app.client.conversations[app.client.current_conversation].values(0)
              self.chat.entry_widget.value = []
              self.chat.display()
            else:
              app.client.current_conversation = None
              self.chat_list.values = []
              self.chat_list.entry_widget.value = []
              self.chat_list.display()
              self.new_chat()
      self.delete_chat_mode = False

    else:
      self.input.invoke()

    self.input.label_widget.value = "Prompt:"
    self.input.value = ""
    self.input.display()

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
  try:
    client = Client()
    app = App(client)
    client.max_yx = app.get_chat_max_yx
    app.run()
  except KeyboardInterrupt:
    pass


if __name__=="__main__":
  import sys
  if len(sys.argv) > 1:
    main(*(sys.argv[1:]))
  else:
    main(*[])
