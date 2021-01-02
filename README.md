# nvim-todo

User interface to todo.txt files.
For convenience, this works with files matching `*.todo`.


## Features

- Parse text lines respecting [todo.txt format](https://github.com/todotxt/todo.txt)
- Smart ordering: higher-priority stuff first, done stuff last
- Smart highlighting: higher-priority in red, done in dark gray
- Mark/unmark as done with `<cr>` (`return`)
- Auto date completion on item creation


## Installation

Install sly for python:

```bash
pip3 install sly
```

Add the following to your neovim config file (eg: `~/.config/nvim/init.vim`):

```
Plug 'Afoucaul/nvim-todo', {'do': ':UpdateRemotePlugins'}
```

Then you can add this to your shell config file (eg: `~/.bashrc` or `~/.zshrc`):


```bash
alias todo='nvim ~/.todo'`
```


## TODO

- [ ] Include sly into installation
- [ ] Implement filtering
- [ ] Insert creation date upon `<cr>` in insert mode
