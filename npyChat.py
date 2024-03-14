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
  def onStart(self):
    #npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
    self.addForm("MAIN", MainForm, name="Open AI Chat")


class ChatView(npyscreen.BoxTitle):
  _contained_widget = npyscreen.Pager


class MainForm(npyscreen.Form):
  def create(self):
    y, x = self.useable_space()
    obj = self.add(
    			  npyscreen.BoxTitle,
    			  name="Chats",
            custom_highlighting=True,
            values=["first line", "second line"],
            rely=1,
            relx=2,
            max_width=25,
            max_height=y-4
          )
    self.chat = self.add(
    	ChatView,
    	name="Conversation",
    	relx=28,
    	rely=1,
    	max_width=x-30,
    	max_height=y-4,
    	values=[
    	  "💬 ❭❭ Hallo 1",
    	  "",
    	  "🤖 ❬❬ Antwort 2"
    	]
    )
    self.input = self.add(
      npyscreen.TitleText,
      name="Prompt:",
      relx=3,
      rely=y-3
    )


def main(args):
  app = App()
  app.run()


if __name__=="__main__":
  import sys
  if len(sys.argv) > 1:
    main(sys.argv[1:])
  else:
    main([])
