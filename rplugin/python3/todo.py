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

    def __str__(self):
        segments = []

        if self.done:
            segments.append("x")
        if self.priority is not None:
            segments.append(f"({self.priority})")
        if self.completion_date is not None:
            segments.append(self.completion_date)
        if self.creation_date is not None:
            segments.append(self.creation_date)
        segments.append(self.description)
        for tag in (self.project_tags or []):
            segments.append(tag)
        for tag in (self.context_tags or []):
            segments.append(tag)
        for key, value in (self.metadata or {}).items():
            segments.append(f"{key}:{value}")

        return " ".join(map(format, segments))

    @classmethod
    def from_string(cls, string):
        lexer = TodoLexer()
        parser = TodoParser()
        try:
            return parser.parse(lexer.tokenize(string.strip()))
        except:
            return None


@neovim.plugin
class TodoPlugin(object):
    def __init__(self, nvim: neovim.Nvim):
        self._nvim = nvim
        self._todos = []

    @neovim.command("TodoParse")
    def todo_parse(self):
        todo = TodoItem.from_string(self._nvim.current.line)
        self._nvim.out_write(f"{todo}\n")

    # @neovim.autocmd("TextChange", pattern="*todo.txt", sync=True)
    # def on_text_change(self):
    #     self.parse_todo_items()

    @neovim.autocmd("BufWrite", pattern="*todo.txt", sync=True)
    @neovim.autocmd("BufEnter", pattern="*todo.txt", sync=True)
    def on_write(self):
        self.parse_todo_items()
        self._nvim.current.buffer[:] = [str(item) for item in self._todos]

    def parse_todo_items(self):
        self._todos = []
        for line in self._nvim.current.buffer:
            todo_item = TodoItem.from_string(line)
            if todo_item is not None:
                self._todos.append(todo_item)

        self._todos.sort(key=str)

        with open("/tmp/a", "w") as fd:
            fd.write("\n".join(map(format, self._todos)))


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
    WORD = r"[^@+]\S+"

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
            "creation_date": p.DATE,
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
            "description": " ".join(p.words)
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
