from enum import Enum

Token_Type = Enum('Token_Type', 
                # Encounters unknown token
                 ['ERROR_TOKEN',
                # Text node
                  'TEXT_TOKEN',
                # of form <a>
                  'START_TAG_TOKEN',
                # of form </a>
                  'END_TAG_TOKEN',
                # of form <br/>
                  'SELF_CLOSING_TAG_TOKEN',
                # of form <!--x-->
                  'COMMENT_TOKEN',
                # of form <!DOCTYPE x>
                  'DOCTYPE_TOKEN',
                # Reaches end of file
                  'EOF_TOKEN'])

class Token:

    def __init__(self, type: Token_Type, data: str, attr: dict):
        self.type = type
        self.data = data
        self.attr = attr

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
    
    def __str__(self):
        return f'Token: type:{self.type}, data:{self.data}, attr:{self.attr}'
    
    def __repr__(self):
        return f'Token({self.type}, {self.data}, {self.attr})'