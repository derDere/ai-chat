"""A module for custom controls
"""


import npyscreen
import base


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
    app:base.AppBase = self.find_parent_app()
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
