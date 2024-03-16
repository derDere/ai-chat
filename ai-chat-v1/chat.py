""" This is just a test app that was used to ask for a python code and directly execute it.
    I fiddled around with it a lot tho
"""


#import openai as oai
import os.path
from openai import OpenAI


class Color:
  """ Just Some Terminal Colors
  """
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKCYAN = '\033[96m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'


class App:
  """Main App Class
  """

  def __init__(self) -> None:
    # OLD oai.api_key = ""
    #oai.api_key = ""
    #oai.api_key = ""
    #model_engine = "text-davinci-003"
    #model_engine = "gpt-4"
    self.model_engine:str = "gpt-3.5-turbo-0125"
    self.response:str = "# no Code"

  def run(self, code:str) -> None:
    """Runs the given code

    Args:
        code (str): The code to run
    """
    print(Color.OKGREEN + "_______________________________\n> Running Task ..." + Color.ENDC)
    try:
      #exec(code)
      print(code)
    except KeyboardInterrupt:
      print(Color.OKCYAN + "\nTask Canceled" + Color.ENDC)
    except Exception as e:
      print(Color.FAIL)
      print(e)
      print(Color.ENDC)

  def loop(self) -> None:
    """Main Loop
    """
    client = OpenAI()

    while True:

      prompt = input(Color.OKGREEN + "> What task do you need?\n" + Color.ENDC + ": ")

      if prompt.lower() == "exit":
        break

      if prompt.lower() == "save":
        while True:
          filename = input("Enter filename: ")
          if os.path.exists(filename):
            print(Color.WARNING + "File already exists!\nChoose a different name!" + Color.ENDC)
          else:
            with open(filename, "w+", encoding="utf-8") as f:
              print(self.response, file=f)
            break
        continue

      if prompt.lower() == "last":
        print(Color.OKGREEN + "_______________________________\n> Last Code:" + Color.ENDC)
        print(f"{Color.OKBLUE}\n{self.response}\n{Color.ENDC}")

      elif prompt.lower() == "repeat" or len(prompt) == 0:
        self.run(self.response)

      else:
        completion = client.chat.completions.create(
          model=self.model_engine,
          #messages=[{"role":"user", "content":"A python code that:\n\n" + prompt + "\n\nand outputs its results."}],
          messages=[{"role":"user", "content":prompt}]
          #max_tokens=(4097-119),
          #n=1,
          #stop=None,
          #temperature=0.5
        )
        self.response = f"{completion.choices[0].message.content}"

        self.run(self.response)

      print(Color.OKGREEN + "_______________________________" + Color.ENDC)


if __name__ == "__main__":
  import sys
  app = App()
  app.loop()
  print(Color.OKGREEN + "_______________________________\n> Goodbye!" + Color.ENDC)
  sys.exit(0)
