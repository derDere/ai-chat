"""The main application class
"""


import client as oaic
import base
import mainform


class App(base.AppBase):
  """The main application class
  """
  client:base.ClientBase
  form:base.MainFormBase

  def __init__(self, client:oaic.Client) -> None:
    super().__init__()
    self.client = client
    self.form = None

  def onStart(self) -> None:
    """Start the application
    """
    #npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
    self.form = self.addForm("MAIN", mainform.MainForm, name="Open AI Chat")

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
