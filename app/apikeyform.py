""" Contains the InputOpenAIAPIKey class and EnterApiKeyApp class.
"""


import npyscreen


class InputOpenAIAPIKey(npyscreen.ActionForm):
  """ Form for entering the OpenAI API key.
  """
  def create(self):
    margin_l = 5
    self.add(npyscreen.FixedText, value="", editable=False, relx=margin_l)
    self.add(npyscreen.FixedText, value="To access OpenAI's API, you need an API key.", editable=False, relx=margin_l)
    self.add(npyscreen.FixedText, value="You can obtain your API key from the OpenAI website.", editable=False, relx=margin_l)
    self.add(npyscreen.FixedText, value="", editable=False, relx=margin_l)
    self.add(npyscreen.FixedText, value="To avoid this dialog save your api key to", editable=False, relx=margin_l)
    self.add(npyscreen.FixedText, value="the environment variable OPENAI_API_KEY", editable=False, relx=margin_l)
    self.add(npyscreen.FixedText, value="", editable=False, relx=margin_l)
    self.add(npyscreen.FixedText, value="", editable=False, relx=margin_l)
    self.add(npyscreen.FixedText, value="Please enter your OpenAI API Key:", editable=False, relx=margin_l)
    self.add(npyscreen.FixedText, value="", editable=False, relx=margin_l)
    self.key_input = self.add(npyscreen.TitleText, name=".........Key:", value="<YOUR_API_KEY>", color='IMPORTANT', relx=margin_l)
    self.add(npyscreen.FixedText, value="", editable=False, relx=margin_l)
    self.add(npyscreen.FixedText, value="", editable=False, relx=margin_l)
    self.url_btn = self.add(npyscreen.Button, name="https://platform.openai.com/api-keys", color='IMPORTANT', relx=margin_l)

  def on_ok(self):
    """ Event handler for the OK button.
    """
    key = '' + self.key_input.value
    if len(key) > 5:
      self.parentApp.setNextForm(None)
      self.parentApp.key_entered = (True, key)
      self.parentApp.switchFormNow()
    else:
      npyscreen.notify_confirm("Please enter an API key.", title="Error", form_color='DANGER')

  def on_cancel(self):
    """ Event handler for the Cancel button.
    """
    self.parentApp.setNextForm(None)
    self.parentApp.key_entered = (False, "")
    self.parentApp.switchFormNow()


class EnterApiKeyApp(npyscreen.NPSAppManaged):
  """ Application for entering the OpenAI API key.
  """
  def onStart(self):
    self.addForm("MAIN", InputOpenAIAPIKey, name="OpenAI API Key missing")


def input_openai_api_key():
  """ Function to get the OpenAI API key from the user.
  """
  app = EnterApiKeyApp()
  app.run()
  ok_pressed, api_key = app.key_entered
  return ok_pressed, api_key
