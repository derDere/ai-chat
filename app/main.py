#!/usr/bin/env python3

"""A ChatGPT Chat Application
"""


import client as oaic
import application


def main(*_:list[str]) -> None:
  """The main function

  Args:
      args (list[str]): The command line arguments
  """
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
