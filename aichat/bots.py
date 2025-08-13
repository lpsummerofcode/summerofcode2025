
class Bot:
    def __init__(self, name: str, avatar:str, description: str):
        self.name = name
        self.avatar= avatar
        self.description = description
        self.messages = []
    
    def append_message(self, message: str):
        self.messages.append(message)
        
