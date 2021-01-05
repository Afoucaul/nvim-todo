" Filetype
au BufNewFile,BufRead *.todo set filetype=todotxt


" Syntax
if exists("b:current_syntax")
    finish
endif

syntax match todotxtContextTag "\v\@\S+"
syntax match todotxtProjectTag "\v\+\S+"
syntax match todotxtMetadataEntry "\v\S+:\S+"

syntax match todotxtPriorityA "\v^(x )?\s*\(A\).*$" contains=ALL
syntax match todotxtPriorityB "\v^(x )?\s*\(B\).*$" contains=ALL
syntax match todotxtPriorityC "\v^(x )?\s*\(C\).*$" contains=ALL

syntax match todotxtDone "\v^x .*$"

hi def todotxtpriorityA ctermfg=DarkRed
hi def todotxtpriorityB ctermfg=DarkYellow
hi def todotxtpriorityC ctermfg=DarkGreen

hi def todotxtDone ctermfg=darkgray gui=strikethrough

hi def todotxtContextTag ctermfg=LightBlue
hi def todotxtProjectTag ctermfg=Magenta
hi def todotxtMetadataEntry ctermfg=DarkBlue

let b:current_syntax = "todotxt"


" Commands
autocmd FileType todotxt nnoremap <silent> <cr> :TodoToggle<cr>
