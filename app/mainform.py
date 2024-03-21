"""The main form for the chat application
"""


import curses
import npyscreen
import controls
import conversation
import base


class MainForm(base.MainFormBase):
  """The main form for the chat application
  """
  chat_list:controls.SelectList
  chat:controls.ChatView
  input:controls.InputField
  editw:int
  delete_chat_mode:bool
  rename_chat_mode:bool
  created:bool
  new_chat_btn:npyscreen.ButtonPress
  rename_chat_btn:npyscreen.ButtonPress
  delete_chat_btn:npyscreen.ButtonPress
  quit_btn:npyscreen.ButtonPress

  def create(self) -> None:
    """Create the form
    """
    side_col_width = 30
    self.delete_chat_mode = False
    self.rename_chat_mode = False
    self.created = False
    app:base.AppBase = self.find_parent_app()
    y, x = tuple[int, int](self.useable_space())
    # create input
    self.input:controls.InputField = self.add(
      controls.InputField,
      name="Prompt:        ",
      relx=side_col_width + 4,
      rely=y-3,
      use_two_lines=False,
    )
    # create chat view
    self.chat:controls.ChatView = self.add(
      controls.ChatView,
      name="Conversation",
      relx=side_col_width + 3,
      rely=1,
      max_width=x-side_col_width-5,
      max_height=y-4,
    )
    # create chat list
    self.chat_list:controls.SelectList = self.add(
      controls.SelectList,
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
    newcon = conversation.Conversation("new", self.find_parent_app().client)
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
    app:base.AppBase = self.find_parent_app()
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
    app:base.AppBase = self.find_parent_app()
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
    app:base.AppBase = self.find_parent_app()
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
