from .tk import Token, Token_Type

class Tokenizer:

    def __init__(self, html: str):
        self.__l = _Lexer(html)
        
    def next(self) -> Token_Type:
        """advances to the next Token
        Returns:
            Token_Type: of next token
        """
        self.__cur_token = self.__l.next_token()
        return self.__cur_token.type
    
    def token(self) -> Token:
        """
        Returns:
            Token: current token
        """
        return self.__cur_token

class _Lexer:

    def __init__(self, html: str):
        self.input = html
        self.position = 0
        self.read_position = 0
        self.ch = ''

    def read_char(self, iter: int = 1):
        """advances position by one, updating the current character
        args:
            iter: number of characters to read, default = 1
        """
        if self.read_position >= len(self.input):
            self.ch = ''
            return

        for _ in range(iter):
            self.ch = self.input[self.read_position]
            self.position = self.read_position
            self.read_position += 1
    
    def next_token(self) -> Token:
        """parses the next token

        Returns:
            Token: all types of tokens
        """
        if self.ch == '':
            self.read_char()

        self.eat_whitespace()

        if self.ch == '':
            return self.eof_token()

        if self.ch != '<':
            return self.read_text_token()

        self.read_char()

        match self.ch:
            case '!':
                match self.peek():
                    case 'D': return self.read_doctype()
                    case '-': return self.read_comment()
                    case  _ : return self.err_token()
            case '/':
                return self.read_end_tag()
            case _:
                return self.read_attributed_tag()
    
    def read_attributed_tag(self) -> Token: 
        """reads a start tag or self closing tag

        Returns:
            Token: either start, self closing, or error tag
        """
        tag = self.read_text(' ', '/', '>')

        self.eat_whitespace()
        attr = {}
        while self.ch != '/' and self.ch != '>':
            self.eat_whitespace()
            key, val = self.read_attribute()
            attr[key] = val
        
        match self.ch:
            case '/':
                self.read_char(2)
                return Token(Token_Type.SELF_CLOSING_TAG_TOKEN, tag, attr)
            case '>':
                self.read_char()
                return Token(Token_Type.START_TAG_TOKEN, tag, attr)
    

    def read_attribute(self) -> tuple:
        """reads an attribute in start or self closing tag

        Returns:
            tuple: of key (i.e. class, id, src, etc.) and val [str] of values of the attribute
        """
        key = self.read_text('=', ' ')
        self.eat_whitespace()
        self.read_char() # equal sign
        self.eat_whitespace()
        self.read_char() # first quote
        val = self.read_text('\"').split()
        self.read_char() # second quote
        self.eat_whitespace()
        return key, val

    def read_end_tag(self) -> Token:
        self.read_char()
        tok = Token(Token_Type.END_TAG_TOKEN, self.read_text('>', ''), {})
        self.read_char()
        return tok
    
    def read_doctype(self) -> Token:
        """reads doctype tag

        Returns:
            Token: either doctype or error
        """
        doctype_str = self.read_text(' ')
        if doctype_str != '!DOCTYPE':
            return self.err_token()
        self.eat_whitespace()
        doctype = self.read_text('>')
        self.read_char()
        return Token(Token_Type.DOCTYPE_TOKEN, doctype, {})
    
    def read_comment(self) -> Token:
        """reads comment tag

        Returns:
            Token: either comment or error tag
        """
        start_comment = self.eat_text('!','-')
        if start_comment != '!--':
            return self.err_token()
        
        comment = self.read_text('-')

        end_comment = self.read_text('>')
        if end_comment != '--':
            return self.err_token()

        self.read_char()
        return Token(Token_Type.COMMENT_TOKEN, comment, {})
    
    def read_text_token(self) -> Token:
        """reads text 

        Returns:
            Token: text token
        """
        return Token(Token_Type.TEXT_TOKEN, self.read_text('<', '').strip(), {})
        
    def peek(self) -> str:
        """gets next char without advancing position

        Returns:
            str: char corresponding with read position
        """
        if self.read_position >= len(self.input):
            return ''
        else:
            return self.input[self.read_position]

    def eat_whitespace(self):
        """advances position past whitespace
        """
        while self.ch == ' '  or \
              self.ch == '\n' or \
              self.ch == '\r' or \
              self.ch == '\t':

            self.read_char()
    
    def read_text(self, *stop_at: str) -> str:
        """reads text until a character with 'stop_at' is specified
        Args:
            stop_at: list of characters to stop read at
        Returns:
            str: text read
        """
        position = self.position
        while self.ch not in stop_at:
            self.read_char()
        return self.input[position:self.position]
    
    def eat_text(self, *eat: str) -> str:
        """advances positon past all characters specified
        Args:
            eat: list of characters to go past
        Returns:
            str: text eaten
        """
        position = self.position
        while self.ch in eat:
            self.read_char()
        return self.input[position:self.position]
    
    def err_token(self) -> Token:
        """return error token

        Returns:
            Token: error token
        """
        return Token(Token_Type.ERROR_TOKEN, '', {})
    
    def eof_token(self) -> Token:
        """return end of file token

        Returns:
            Token: eof token
        """
        return Token(Token_Type.EOF_TOKEN, '', {})
