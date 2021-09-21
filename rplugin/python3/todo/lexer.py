import datetime as dt

import sly


class TodoLexer(sly.Lexer):
    tokens = {
        X,
        PRIORITY,
        DATE,
        PROJECT_TAG,
        CONTEXT_TAG,
        WORD,
        METADATA,
    }

    ignore = " \t\n\r"

    X = r"x\s"
    PRIORITY = r"\([A-Z]\)"
    DATE = r"\d{4}-\d{2}-\d{2}"
    PROJECT_TAG = r"\+[\w-]+"
    CONTEXT_TAG = r"@[\w-]+"
    METADATA = r"[\w-]+:[\w-]+"
    WORD = r"[^@+\s]\S*"

    def METADATA(self, token: sly.lex.Token) -> sly.lex.Token:
        key, value = token.value.split(":")
        token.value = {key: value}
        return token

    def DATE(self, token: sly.lex.Token) -> sly.lex.Token:
        token.value = dt.date.fromisoformat(token.value)
        return token

    def PRIORITY(self, token: sly.lex.Token) -> sly.lex.Token:
        token.value = token.value[1]
        return token
