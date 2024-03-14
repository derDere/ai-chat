from openai import OpenAI
import os.path


#model_engine = "gpt-3.5-turbo-0125"
#
#client = OpenAI()
#
#    completion = client.chat.completions.create(
#      model=model_engine,
#      #messages=[{"role":"user", "content":"A python code that:\n\n" + prompt + "\n\nand outputs its results."}],
#      messages=[{"role":"user", "content":prompt}]
#      #max_tokens=(4097-119),
#      #n=1,
#      #stop=None,
#      #temperature=0.5
#    )
#    response = completion.choices[0].message.content


#!/usr/bin/env python3
import npyscreen
import random


class Conversation:
  def __init__(self, name):
    self.name:str = name
    self.messages:list[dict[str,str]] = []
    self.maxX = -1

  def add(self, message):
    self.messages.append(message)

  def values(self):
    prefixes = {
      "user": " 💬 ❭❭ ",
      "system": "    🤖 ❬❬ "
    }
    values = []
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
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.model = "gpt-3.5-turbo-0125"
    self.conversations:dict[str, Conversation] = {}
    self.current_conversation:str = "New Chat"
    self.conversations[self.current_conversation] = Conversation(self.current_conversation)

  def get_conversation(self) -> list[str]:
    l = []
    for convKey in self.conversations:
      l.append(self.conversations[convKey].name)
    return l

  def send(self, conv_key, prompt) -> None:
    if conv_key not in self.conversations:
      self.conversations[conv_key] = Conversation(conv_key)
    conv = self.conversations[conv_key]
    messages = conv.messages
    messages.append({"role":"user", "content":prompt})
    completion = self.chat.completions.create(
      model=self.model,
      messages=messages
    )
    conv.messages.append({"role":"system", "content":completion.choices[0].message.content})


class color:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKCYAN = '\033[96m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'


class App(npyscreen.NPSAppManaged):
  def __init__(self, client):
    super().__init__()
    self.client = client

  def onStart(self):
    #npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
    self.form = self.addForm("MAIN", MainForm, name="Open AI Chat")


class ChatView(npyscreen.BoxTitle):
  _contained_widget = npyscreen.Pager


class InputField(npyscreen.TitleText):
  def invoke(self):
    app = self.find_parent_app()
    app.client.send(app.client.current_conversation, self.value)
    conv = app.client.conversations[app.client.current_conversation]
    chat_view = app.form.chat
    chat_view.values = conv.values()
    chat_view.display()
    self.value = ""
    self.display()


class MainForm(npyscreen.Form):
  def create(self):
    app = self.find_parent_app()
    y, x = self.useable_space()
    self.chat_list = self.add(
      npyscreen.BoxTitle,
      name="Chats",
      custom_highlighting=True,
      values=app.client.get_conversation(),
      rely=1,
      relx=2,
      max_width=25,
      max_height=y-4,
    )
    self.chat = self.add(
    	ChatView,
    	name="Conversation",
    	relx=28,
    	rely=1,
    	max_width=x-30,
    	max_height=y-4,
    	values=[],
    )
    self.input = self.add(
      InputField,
      name="Prompt:",
      relx=3,
      rely=y-3,
    )
    self.input.add_handlers({
      10: lambda e: self.input.invoke(),
      "^Q": exit
    })
    self.editw = 1


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
