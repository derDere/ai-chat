#!/usr/bin/env python3

"""A ChatGPT Chat Application
"""


import os
import client as oaic
import application
from apikeyform import input_openai_api_key


def main(*_:list[str]) -> None:
  """The main function

  Args:
      args (list[str]): The command line arguments
  """
  # Check if API Key Env Var exists
  if 'OPENAI_API_KEY' not in os.environ:
    ok_pressed, api_key = input_openai_api_key()
    if ok_pressed:
      os.environ['OPENAI_API_KEY'] = api_key
    else:
      print("No API Key provided. Exiting...")
      return
  try:
    client = oaic.Client()
    app = application.App(client)
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
