from typing import Dict, List, Optional

import dataclasses as dc
import datetime as dt

from . import lexer
from . import parser


@dc.dataclass
class TodoItem:
    PRIORITY = ["A", "B", "C"]

    done: bool = False
    description: str = ""
    project_tags: List[str] = dc.field(default_factory=list)
    context_tags: List[str] = dc.field(default_factory=list)
    metadata: Dict[str, str] = dc.field(default_factory=dict)
    creation_date: Optional[dt.date] = None
    completion_date: Optional[dt.date] = None
    priority: Optional[str] = None

    def __str__(self) -> str:
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
        for tag in self.project_tags:
            segments.append(tag)
        for tag in self.context_tags:
            segments.append(tag)
        for key, value in self.metadata.items():
            segments.append(f"{key}:{value}")

        return " ".join(map(format, segments))

    def increase_priority(self) -> None:
        if self.priority is None:
            self.priority = "A"
        else:
            priority_i = self.PRIORITY.index(self.priority) - 1
            self.priority = self.PRIORITY[max(priority_i, 0)]

    def decrease_priority(self) -> None:
        if self.priority is None:
            self.priority = "C"
        else:
            priority_i = self.PRIORITY.index(self.priority) + 1
            self.priority = self.PRIORITY[min(priority_i, len(self.PRIORITY) - 1)]

    @classmethod
    def from_string(cls, string: str) -> "TodoItem":
        todo_lexer = lexer.TodoLexer()
        todo_parser = parser.TodoParser()
        try:
            result = todo_parser.parse(todo_lexer.tokenize(string.strip()))
            if result.done and result.creation_date and not result.completion_date:
                result.completion_date = dt.date.today()
            return result

        except:
            return None
