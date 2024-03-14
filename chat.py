#import openai as oai
from openai import OpenAI
import os.path

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

# OLD oai.api_key = ""
#oai.api_key = ""
#oai.api_key = ""

#model_engine = "text-davinci-003"
#model_engine = "gpt-4"
model_engine = "gpt-3.5-turbo-0125"

response = "# no Code"

def run(code):
  print(color.OKGREEN + "_______________________________\n> Running Task ..." + color.ENDC)
  try:
    #exec(code)
    print(code)
  except KeyboardInterrupt as Ki:
    print(color.OKCYAN + "\nTask Canceled" + color.ENDC)
  except Exception as e:
    print(color.FAIL)
    print(e)
    print(color.ENDC)

client = OpenAI()

while True:

  prompt = input(color.OKGREEN + "> What task do you need?\n" + color.ENDC + ": ")

  if prompt.lower() == "exit":
    break

  if prompt.lower() == "save":
    while True:
      filename = input("Enter filename: ")
      if os.path.exists(filename):
        print(color.WARNING + "File already exists!\nChoose a different name!" + color.ENDC)
      else:
        with open(filename, "w+", encoding="utf-8") as f:
          print(response, file=f)
        break
    continue

  if prompt.lower() == "last":
    print(color.OKGREEN + "_______________________________\n> Last Code:" + color.ENDC)
    print(color.OKBLUE + "\n" + response + "\n" + color.ENDC)

  elif prompt.lower() == "repeat" or len(prompt) == 0:
    run(response)

  else:
    completion = client.chat.completions.create(
      model=model_engine,
      #messages=[{"role":"user", "content":"A python code that:\n\n" + prompt + "\n\nand outputs its results."}],
      messages=[{"role":"user", "content":prompt}]
      #max_tokens=(4097-119),
      #n=1,
      #stop=None,
      #temperature=0.5
    )
    response = completion.choices[0].message.content

    run(response)

  print(color.OKGREEN + "_______________________________" + color.ENDC)
