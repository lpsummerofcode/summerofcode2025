
class Bot:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.messages = []
    
    def append_message(self, message: str):
        self.messages.append(message)

