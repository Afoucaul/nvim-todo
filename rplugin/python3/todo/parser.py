import sly

from . import todo_item
from . import lexer


class TodoParser(sly.Parser):
    tokens = lexer.TodoLexer.tokens

    start = "todo"

    @_("description")
    def todo(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return todo_item.TodoItem(
            **p.description,
        )

    @_("header description")
    def todo(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return todo_item.TodoItem(
            **p.header,
            **p.description,
        )

    @_("description tags")
    def todo(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return todo_item.TodoItem(
            **p.description,
            **p.tags,
        )

    @_("header description tags")
    def todo(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return todo_item.TodoItem(
            **p.header,
            **p.description,
            **p.tags,
        )

    @_("X PRIORITY")
    def header(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return {
            "done": True,
            "priority": p.PRIORITY,
        }

    @_("X dates")
    def header(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return {
            "done": True,
            **p.dates,
        }

    @_("X PRIORITY dates")
    def header(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return {
            "done": True,
            "priority": p.PRIORITY,
            **p.dates,
        }

    @_("PRIORITY dates")
    def header(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return {
            "priority": p.PRIORITY,
            **p.dates,
        }

    @_("X")
    def header(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return {
            "done": True,
        }

    @_("PRIORITY")
    def header(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return {
            "priority": p.PRIORITY,
        }

    @_("dates")
    def header(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return {
            **p.dates,
        }

    @_("DATE")
    def dates(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return {
            "creation_date": p.DATE,
        }

    @_("DATE DATE")
    def dates(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return {
            "creation_date": p.DATE0,
            "completion_date": p.DATE1,
        }

    @_("words")
    def description(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return {
            "description": " ".join(p.words)
        }

    @_("WORD words")
    def words(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return [p.WORD] + p.words

    @_("WORD")
    def words(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return [p.WORD]

    @_("tags tags")
    def tags(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return {
            "project_tags": p.tags0.get("project_tags", []) + p.tags1.get("project_tags", []),
            "context_tags": p.tags0.get("context_tags", []) + p.tags1.get("context_tags", []),
            "metadata": {**p.tags0.get("metadata", {}), **p.tags1.get("metadata", {})},
        }

    @_("PROJECT_TAG")
    def tags(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return {"project_tags": [p.PROJECT_TAG]}

    @_("CONTEXT_TAG")
    def tags(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        return {"context_tags": [p.CONTEXT_TAG]}

    @_("METADATA")
    def tags(self, p: sly.yacc.YaccProduction) -> sly.yacc.YaccProduction:
        key, value = p.METADATA.split(":")
        return {"metadata": {key: value}}
