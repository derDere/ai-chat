"""A client for the OpenAI ChatGPT API
"""


from typing import Callable
import functions
import conversation
import base


class Client(base.ClientBase):
  """A client for the OpenAI ChatGPT API
  """
  model:str
  conversations:dict[str, conversation.Conversation]
  current_conversation:str

  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.model = "gpt-3.5-turbo-0125"
    self.conversations:dict[str, conversation.Conversation] = {}
    self.current_conversation:str = None
    #self.conversations[self.current_conversation] = Conversation(self.current_conversation, self)
    #self.conversations["chat2"] = Conversation("chat2", self)
    self.max_yx:Callable[[], int] = lambda: 20, 80
    conversation_list = functions.list_conversation_files()
    for [key, path] in conversation_list.items():
      conv = conversation.Conversation(key, self)
      conv.load(path)
      self.conversations[key] = conv
    if len(self.conversations) > 0:
      self.current_conversation = list(self.conversations.keys())[0]

  def get_conversation(self) -> list[str]:
    """Get a list of conversation names
    """
    l:list[str] = []
    if self.conversations is None:
      self.conversations = {}
    for [_, conv] in self.conversations.items():
      l.append(conv.name)
    return l

  def send(self, conv_key:str, prompt:str) -> None:
    """Send a message to the chat model

    Args:
        conv_key (str): The conversation key
        prompt (str): The message to send
    """
    prompt = prompt.strip()
    if len(prompt) == 0:
      return
    conv:conversation.Conversation
    if conv_key is None:
      conv = conversation.Conversation("<<new>>", self)
    elif conv_key not in self.conversations:
      self.conversations[conv_key] = conversation.Conversation(conv_key, self)
      conv = self.conversations[conv_key]
    else:
      conv = self.conversations[conv_key]
    messages = conv.messages
    messages.append({"role": "user", "content": prompt})
    completion = self.chat.completions.create(
      model=self.model,
      messages=messages
    )
    conv.messages.append({"role":"system", "content":completion.choices[0].message.content})
    if conv_key is None:
      # get conv name
      name_completion = self.chat.completions.create(
        model=self.model,
        messages= messages + [{
          "role": "user",
          "content": "Generate a name for this conversation. " +
                    "Max of 25 characters and UpperCamelCase! " +
                    "Your answer should only contain this name! " +
                    "No formatting not special characters!"
        }],
      )
      conv_key = name_completion.choices[0].message.content
      conv.name = conv_key
      self.conversations[conv_key] = conv
    conv.save()
    return conv_key
