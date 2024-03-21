"""Contains all display texts and labels for the application.
"""


import locale


ZERO_WIDTH_SPACE = "" #\u200B" # Fixes string length with emojis


# EMOJI ICONS
#ICON_AI = "🤖" + ZERO_WIDTH_SPACE
#ICON_USER = "💬" + ZERO_WIDTH_SPACE
#ICON_WAIT = "⏳" + ZERO_WIDTH_SPACE

# Ascii ICONS
#ICON_AI = "[°_°]"
#ICON_USER = "(^.^)"
#ICON_WAIT = "}{"

# NerdFont ICONS
ICON_AI = "ﮧ"
ICON_USER = ""
ICON_WAIT = "ﮫ"

# Text ICONS
#ICON_AI = "AI"
#ICON_USER = "ME"
#ICON_WAIT = "..."


class LabelsBase:
  """Base class for all languages.
  """
  # General
  app_title = "app_title"
  # Main Form
  main_form_chat_list_title = "main_form_chat_list_title"
  main_form_conversation_title = "main_form_conversation_title"
  main_form_prompt_title = "main_form_prompt_title"
  main_form_newchat_title = "main_fomr_newchat_title"
  main_form_renamechat_title = "main_form_renamechat_title"
  main_form_deletechat_title = "main_form_deletechat_title"
  main_form_deletechat_message = "main_form_deletechat_message"
  main_form_newchat_button = "main_form_newchat_button"
  main_form_renamechat_button = "main_form_renamechat_button"
  main_form_deletechat_button = "main_form_deletechat_button"
  main_form_quit_button = "main_form_quit_button"
  # Conversations
  conversation_new_conversation_line1 = "conversation_new_conversation_line1"
  conversation_new_conversation_line2 = "conversation_new_conversation_line2"
  conversation_user_prefix = "conversation_user_prefix"
  conversation_system_prefix = "conversation_system_prefix"
  conversation_generated_response = "conversation_generated_response"


class LangEN(LabelsBase):
  """English language labels.
  """
  def __init__(self) -> None:
    super().__init__()
    # General
    self.app_title = "Open AI Chat"
    # Main Form
    self.main_form_chat_list_title = "Chats"
    self.main_form_conversation_title = "Conversation"
    self.main_form_prompt_title =     "Prompt:          "
    self.main_form_newchat_title =    "New Chat:        "
    self.main_form_renamechat_title = "Rename Chat:     "
    self.main_form_deletechat_title = "Delete Chat:     "
    self.main_form_deletechat_message = "type in DELETE to confirm"
    self.main_form_newchat_button =    "[     + New Chat      (^N) ]"
    self.main_form_renamechat_button = "[     Rename Chat     (^R) ]"
    self.main_form_deletechat_button = "[     Delete Chat     (^D) ]"
    self.main_form_quit_button =       "[        Quit         (^Q) ]"
    # Conversations
    self.conversation_new_conversation_line1 = "    NEW CONVERSATION "
    self.conversation_new_conversation_line2 = "    > waiting for prompt ... "
    self.conversation_user_prefix = f" {ICON_USER} ❭❭ "
    self.conversation_system_prefix = f"    {ICON_AI} ❬❬ "
    self.conversation_generated_response = f"{ICON_WAIT} GENERATING RESPONSE ..."


class LangDE(LabelsBase):
  """German language labels.
  """
  def __init__(self) -> None:
    super().__init__()
    # General
    self.app_title = "Open AI Chat"
    # Main Form
    self.main_form_chat_list_title = "Chats"
    self.main_form_conversation_title = "Konversation"
    self.main_form_prompt_title =     "Eingabe:         "
    self.main_form_newchat_title =    "Neuer Chat:      "
    self.main_form_renamechat_title = "Chat umbenennen: "
    self.main_form_deletechat_title = "Chat löschen:    "
    self.main_form_deletechat_message = "tippe DELETE um zu bestätigen"
    self.main_form_newchat_button =    "[    + Neuer Chat     (^N) ]"
    self.main_form_renamechat_button = "[   Chat umbenennen   (^R) ]"
    self.main_form_deletechat_button = "[     Chat löschen    (^D) ]"
    self.main_form_quit_button =       "[       Beenden       (^Q) ]"
    # Conversations
    self.conversation_new_conversation_line1 = "    NEUE KONVERSATION "
    self.conversation_new_conversation_line2 = "    > warte auf Eingabe ... "
    self.conversation_user_prefix = f" {ICON_USER} ❭❭ "
    self.conversation_system_prefix = f"    {ICON_AI} ❬❬ "
    self.conversation_generated_response = f"{ICON_WAIT} ANTWORT WIRD GENERIERT ..."


class LangFR(LabelsBase):
  """French language labels.
  """
  def __init__(self) -> None:
    super().__init__()
    # General
    self.app_title = "Open AI Chat"
    # Main Form
    self.main_form_chat_list_title = "Chats"
    self.main_form_conversation_title = "Conversation"
    self.main_form_prompt_title =     "Prompt:          "
    self.main_form_newchat_title =    "Nouveau chat:    "
    self.main_form_renamechat_title = "Renommer chat:   "
    self.main_form_deletechat_title = "Supprimer chat:  "
    self.main_form_deletechat_message = "tapez DELETE pour confirmer"
    self.main_form_newchat_button =    "[   + Nouveau Chat    (^N) ]"
    self.main_form_renamechat_button = "[    Renommer Chat    (^R) ]"
    self.main_form_deletechat_button = "[   Supprimer Chat    (^D) ]"
    self.main_form_quit_button =       "[       Quitter       (^Q) ]"
    # Conversations
    self.conversation_new_conversation_line1 = "    NOUVELLE CONVERSATION "
    self.conversation_new_conversation_line2 = "    > en attente de l'invite ... "
    self.conversation_user_prefix = f" {ICON_USER} ❭❭ "
    self.conversation_system_prefix = f"    {ICON_AI} ❬❬ "
    self.conversation_generated_response = f"{ICON_WAIT} GÉNÉRATION DE LA RÉPONSE ..."


class Labels:
  """A class for managing language labels.
  """
  def __init__(self) -> None:
    self.en:LabelsBase = LangEN()
    self.de:LabelsBase = LangDE()
    self.fr:LabelsBase = LangFR()
    self.cur:LabelsBase = self.en # use LabelsBase() for debug
    self.set_by_system_lang()

  def get(self, label:str) -> str:
    """Get a label
    """
    return getattr(self.cur, label)

  def set_lang(self, lang:str) -> None:
    """Set the current language
    """
    self.cur = getattr(self, lang)

  def set_by_system_lang(self) -> None:
    """Set the language by the system language
    """
    lang, _ = locale.getdefaultlocale()
    if lang == "de_DE":
      self.set_lang("de")
    elif lang == "fr_FR":
      self.set_lang("fr")
    else:
      self.set_lang("en")


# export language labels
Lang = Labels()
