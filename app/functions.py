"""This module contains functions for the app
"""


import os
from constants import CONVERSATIONS_FOLDER_PATH, FILE_EXTENSION


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
  path = get_home_folder() + CONVERSATIONS_FOLDER_PATH
  create_folder(path)
  conversations = {}
  files = os.listdir(path)
  for file in files:
    if file.endswith(FILE_EXTENSION):
      key = file.replace(FILE_EXTENSION, "")
      file_path = path + file
      conversations[key] = file_path
  return conversations
