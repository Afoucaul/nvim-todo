import dataclasses as dc
import datetime as dt
import re

import neovim
import sly


@dc.dataclass
class TodoItem:
    done: bool = False
    description: str = ""
    project_tags: [str] = dc.field(default_factory=list)
    context_tags: [str] = dc.field(default_factory=list)
    metadata: {str: str} = dc.field(default_factory=dict)
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
            result = parser.parse(lexer.tokenize(string.strip()))
            if result.done and result.creation_date and not result.completion_date:
                result.completion_date = dt.date.today()
            return result
        except:
            return None


@neovim.plugin
class TodoPlugin(object):
    def __init__(self, nvim: neovim.Nvim):
        self._nvim = nvim

    @neovim.command("TodoLex")
    def todo_lex(self):
        line = self._nvim.current.line
        lexer = TodoLexer()
        tokens = lexer.tokenize(line)
        self._nvim.out_write(f"{list(tokens)}\n")

    @neovim.command("TodoParse")
    def todo_parse(self):
        todo = TodoItem.from_string(self._nvim.current.line)
        self._nvim.out_write(f"{todo}\n")

    @neovim.command("TodoToggle", sync=True)
    def todo_toggle(self):
        item = TodoItem.from_string(self._nvim.current.line)
        item.done = not item.done
        item.completion_date = dt.date.today() if item.done else None
        self._nvim.current.line = str(item)
        self.todo_sort()

    @neovim.command("TodoSort")
    def todo_sort(self):
        todos = self.parse_todo_items()
        todos.sort(key=str)
        self._nvim.current.buffer[:] = [str(item) for item in todos]

    @neovim.command("TodoSearch", nargs="+")
    def todo_search(self, args):
        search_result = self.search(*args)
        if search_result:
            lines = "\n".join(map(str, search_result))
            command = f"echo '{lines}'\n"
            self._nvim.command(command)

    def search(self, *args):
        todo_items = self.parse_todo_items()
        for arg in args:
            if arg.startswith("@"):
                todo_items = [
                    item
                    for item in todo_items
                    if arg in item.context_tags
                ]
            elif arg.startswith("+"):
                todo_items = [
                    item
                    for item in todo_items
                    if arg in item.project_tags
                ]
            elif re.match(r"[\w-]+:[\w-]+", arg):
                key, value = arg.split(":")
                todo_items = [
                    item
                    for item in todo_items
                    if item.metadata.get(key) == value
                ]

        return todo_items

    @neovim.autocmd("BufWrite", pattern="*.todo", sync=True)
    def on_write(self):
        self.todo_sort()

    @neovim.autocmd("InsertEnter", pattern="*.todo", sync=False)
    def on_insert_enter(self):
        if not self._nvim.current.line:
            item = TodoItem(creation_date=dt.date.today())
            line = str(item)
            self._nvim.current.line = line
            self._nvim.funcs.cursor(0, len(line) + 1)

    def parse_todo_items(self) -> [TodoItem]:
        todos = []
        for line in self._nvim.current.buffer:
            todo_item = TodoItem.from_string(line)
            if todo_item is not None:
                todos.append(todo_item)

        return todos


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
