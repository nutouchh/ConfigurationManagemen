import json
from sly import Lexer, Parser

"""
files ::= file files | empty
file ::=  group student subject 
group ::= "(" "^" name names  ")"
subject ::= "(" title ")"
student ::= "(" "@" info infooo ")"
title ::= name
"""
class CalcLexer(Lexer):
    tokens = {FIRST_BRACKET, LAST_BRACKET, NAME, STRING, DIGIT, GROUP, STUDENT}

    # Tokens
    FIRST_BRACKET = r'\('
    LAST_BRACKET = r'\)'
    ignore = r' \t'
    ignore_newline = r'\n+'
    ignore_comment = r'\#.*'
    NAME=r'[^ \t\#();\'\@\^]+'
    STRING =r"'[^\:\)\()\t\']*'"
    DIGIT=r'[0-9]+'
    GROUP=r'\^'
    STUDENT=r'\@'

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    # Вычислить столбец.
    # ввод - это входная текстовая строка
    # токен - это экземпляр
    def find_column(text, token):
        last_cr = text.rfind('\n', 0, token.index)
        if last_cr < 0:
            last_cr = 0
        column = (token.index - last_cr) + 1
        return column

    def error(self, t):
        print("Неизвестный токен '%s'" % t.value[0])
        self.index += 1


class CalcParser(Parser):
    debugfile = 'parser.out'
    tokens = CalcLexer.tokens

    @_('empty')
    def files(self, p):
        return []

    @_('file files')
    def files(self, p):
        return [p.file] + p.files

    @_('group student subject')
    def file(self, p):
        return dict(groups=p.group, students=p.student, subject=p.subject)

    @_("FIRST_BRACKET title LAST_BRACKET")
    def subject(self, p):
        return (p.title[1:-1]).replace('\n', 'h')

    @_("FIRST_BRACKET STUDENT info infooo  LAST_BRACKET")
    def student(self, p):
        return [dict(age=int((p.info[:-1]).replace('\n', 'h')[0:2]),
                     group=((p.info[1:-1]).replace('\n', 'h')[2:12]),
                     name=((p.info[1:]).replace('\n', 'h')[12:]))] + p.infooo

    @_("FIRST_BRACKET GROUP name names  LAST_BRACKET")
    def group(self, p):
        return [p.name] + p.names

    @_('info infooo')
    def infooo(self, p):
        return [dict(age=int((p.info[0:-1]).replace('\n', 'h')[0:2]), group=((p.info[1:]).replace('\n', 'h')[2:12]),
                     name=((p.info[1:]).replace('\n', 'h')[12:]))] + p.infooo

    @_('STRING')
    def info(self, p):
        return p[0][1:-1]

    @_('name')
    def title(self, p):
        return '"' + p.name + "'"

    @_('name names')
    def names(self, p):
        return [p.name] + p.names

    @_('empty')
    def infooo(self, p):
        return []

    @_('empty')
    def names(self, p):
        return []

    @_('DIGIT')
    def name(self, p):
        return int(p[0])

    @_('NAME')
    def name(self, p):
        return p[0]

    @_('STRING')
    def name(self, p):
        return p[0][1:-1]

    @_('')
    def empty(self, p):
        pass

if __name__ == '__main__':

    a = 'check.txt'
    f = open(a, 'r', encoding='utf-8')
    text = f.read()
    f.close()
    print(text)

    lexer = CalcLexer()
    parser = CalcParser()

    for tok in lexer.tokenize(text):
        print('type=%r, value=%r' % (tok.type, tok.value))

    data = (parser.parse(lexer.tokenize(text)))
    with open('output.json', 'w') as f:
        f.write(json.dumps(data, indent=3, ensure_ascii=False))
    with open('output.json', 'r') as f:
        for line in f:
            print(line.rstrip())

