from typing import List

import datetime as dt

import neovim

from .lexer import TodoLexer
from .todo_item import TodoItem


@neovim.plugin
class TodoPlugin(object):
    def __init__(self, nvim: neovim.Nvim):
        self._nvim = nvim

    @neovim.command("TodoLex")
    def todo_lex(self) -> None:
        line = self._nvim.current.line
        lexer = TodoLexer()
        tokens = lexer.tokenize(line)
        self._nvim.out_write(f"{list(tokens)}\n")

    @neovim.command("TodoParse")
    def todo_parse(self) -> None:
        todo = TodoItem.from_string(self._nvim.current.line)
        self._nvim.out_write(f"Todo object: {todo}\n")

    @neovim.command("TodoToggle", sync=True)
    def todo_toggle(self) -> None:
        item = TodoItem.from_string(self._nvim.current.line)
        if item is None:
            self._nvim.out_write("Invalid todo format\n")
            return

        item.done = not item.done
        item.completion_date = dt.date.today() if item.done else None
        self._nvim.current.line = str(item)

        go_back_to_previous_position = not item.done
        self.todo_sort(go_back_to_previous_position=go_back_to_previous_position)

    @neovim.command("TodoSort", sync=True)
    def todo_sort(self, *, go_back_to_previous_position: bool = True) -> None:
        cursor_todo = TodoItem.from_string(self._nvim.current.line)
        todos = sorted(self.parse_todo_items(), key=str)
        self._nvim.current.buffer[:] = [str(todo) for todo in todos]

        # Move cursor to previously hovered item
        if go_back_to_previous_position and cursor_todo is not None:
            for i, todo in enumerate(todos, 1):
                if todo == cursor_todo:
                    self._nvim.funcs.cursor(i, 1)
                    break

    @neovim.command("TodoPriorityUp", sync=True)
    def todo_priority_up(self):
        item = TodoItem.from_string(self._nvim.current.line)
        if item is None:
            self._nvim.out_write("Invalid todo format\n")
            return

        item.increase_priority()
        self._nvim.current.line = str(item)
        self.todo_sort()

    @neovim.command("TodoPriorityDown", sync=True)
    def todo_priority_down(self) -> None:
        item = TodoItem.from_string(self._nvim.current.line)
        if item is None:
            self._nvim.out_write("Invalid todo format\n")
            return

        item.decrease_priority()
        self._nvim.current.line = str(item)
        self.todo_sort()

    @neovim.autocmd("BufWrite", pattern="*.todo", sync=True)
    def on_write(self) -> None:
        self.todo_sort()

    @neovim.autocmd("InsertEnter", pattern="*.todo", sync=False)
    def on_insert_enter(self) -> None:
        if not self._nvim.current.line:
            item = TodoItem(creation_date=dt.date.today(), priority="C")
            line = str(item)
            self._nvim.current.line = line
            self._nvim.funcs.cursor(0, len(line) + 1)

    @neovim.autocmd("TextChangedI", pattern="*.todo", sync=False)
    def on_text_changed_i(self) -> None:
        if not self._nvim.current.line:
            item = TodoItem(creation_date=dt.date.today(), priority="C")
            line = str(item)
            self._nvim.current.line = line
            self._nvim.funcs.cursor(0, len(line) + 1)

    def parse_todo_items(self) -> List[TodoItem]:
        todos = []
        for line in self._nvim.current.buffer:
            todo_item = TodoItem.from_string(line)
            if todo_item is not None:
                todos.append(todo_item)

        return todos
