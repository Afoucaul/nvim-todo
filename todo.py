import dataclasses as dc
import datetime as dt
import re

import neovim
import sly


@dc.dataclass
class TodoItem:
    done: bool = False
    description: str = ""
    project_tags: [str] = None
    context_tags: [str] = None
    metadata: {str: str} = None
    creation_date: dt.date = None
    completion_date: dt.date = None
    priority: str = None


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

    X = r"x"
    PRIORITY = r"\([A-Z]\)"
    DATE = r"\d{4}-\d{2}-\d{2}"
    PROJECT_TAG = r"\+\w+"
    CONTEXT_TAG = r"@\w+"
    METADATA = r"\w+:\w+"
    WORD = r"\w+"

    def METADATA(self, token):
        key, value = token.value.split(":")
        token.value = {key: value}
        return token

    def DATE(self, token):
        token.value = dt.date.fromisoformat(token.value)
        return token

    def PRIORITY(self, token):
        token.value = token.value[1]
        return token


class TodoParser(sly.Parser):
    tokens = TodoLexer.tokens

    start = "todo"

    @_("description")
    def todo(self, p):
        return TodoItem(
            **p.description,
        )

    @_("header description")
    def todo(self, p):
        return TodoItem(
            **p.header,
            **p.description,
        )

    @_("description tags")
    def todo(self, p):
        return TodoItem(
            **p.description,
            **p.tags,
        )

    @_("header description tags")
    def todo(self, p):
        return TodoItem(
            **p.header,
            **p.description,
            **p.tags,
        )

    @_("X PRIORITY")
    def header(self, p):
        return {
            "done": True,
            "priority": p.PRIORITY,
        }

    @_("X dates")
    def header(self, p):
        return {
            "done": True,
            **p.dates,
        }

    @_("X PRIORITY dates")
    def header(self, p):
        return {
            "done": True,
            "priority": p.PRIORITY,
            **p.dates,
        }

    @_("PRIORITY dates")
    def header(self, p):
        return {
            "priority": p.PRIORITY,
            **p.dates,
        }

    @_("X")
    def header(self, p):
        return {
            "done": True,
        }

    @_("PRIORITY")
    def header(self, p):
        return {
            "priority": p.PRIORITY,
        }

    @_("dates")
    def header(self, p):
        return {
            **p.dates,
        }

    @_("DATE")
    def dates(self, p):
        return {
            "completion_date": p.DATE,
        }

    @_("DATE DATE")
    def dates(self, p):
        return {
            "creation_date": p.DATE0,
            "completion_date": p.DATE1,
        }

    @_("words")
    def description(self, p):
        return {
            "description": p.words
        }

    @_("WORD words")
    def words(self, p):
        return [p.WORD] + p.words

    @_("WORD")
    def words(self, p):
        return [p.WORD]

    @_("tags tags")
    def tags(self, p):
        return {**p.tags0, **p.tags1}

    @_("PROJECT_TAG")
    def tags(self, p):
        return {"project_tags": [p.PROJECT_TAG]}

    @_("CONTEXT_TAG")
    def tags(self, p):
        return {"context_tags": [p.CONTEXT_TAG]}

    @_("METADATA")
    def tags(self, p):
        return {"metadata": p.METADATA}


TODO_REGEX = re.compile(
    r"(?:(?P<done>^|^x) )?\s*"
    r"(?:\(?P<priority>[A-Z]\) )?\s*"
    r"(?:(?P<completion_date>\d{4}-\d{2}-\d{2}) )?\s*"
    r"(?:(?P<creation_date>\d{4}-\d{2}-\d{2}) )?\s*"
)


def parse_todo_line(line):
    lexer = TodoLexer()
    parser = TodoParser()
    result = parser.parse(lexer.tokenize(line))
    return result
    # return {
    #     "done": False,
    #     "priority": None,
    #     "completion_date": None,
    #     "creation_date": None,
    #     "description": "",
    #     "project_tags": set(),
    #     "context_tags": set(),
    #     "metadata": {},
    # }




@neovim.plugin
class TodoPlugin(object):
    def __init__(self, nvim: neovim.Nvim):
        self._nvim = nvim

    @neovim.command("TodoHello")
    def todo_hello(self):
        self._nvim.current.line = "hello"

    @neovim.autocmd("BufEnter", pattern="*todo.txt")
    def on_enter(self):
        pass


if __name__ == "__main__":
    import sys
    line = " ".join(sys.argv[1:])
    print(parse_todo_line(line))
