
class Bot:
    def __init__(self, name: str, description: str, emoji: str):
        self.name = name
        self.description = description
        self.emoji = emoji
        self.messages = []
    
    def append_message(self, message: str):
        self.messages.append(message)
        
