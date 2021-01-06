if exists("b:current_syntax")
    finish
endif

syntax match todotxtContextTag "\v(\s)@<=\@\S+"
syntax match todotxtOverdueTag "\v(\s)@<=\@overdue"
syntax match todotxtProjectTag "\v(\s)@<=\+\S+"
syntax match todotxtMetadataEntry "\v\S+:\S+"

syntax match todotxtPriorityA "\v^(x )?\s*\(A\).*$" contains=ALL
syntax match todotxtPriorityB "\v^(x )?\s*\(B\).*$" contains=ALL
syntax match todotxtPriorityC "\v^(x )?\s*\(C\).*$" contains=ALL

syntax match todotxtDone "\v^x .*$"


hi def todotxtpriorityA ctermfg=DarkRed
hi def todotxtpriorityB ctermfg=DarkYellow
hi def todotxtpriorityC ctermfg=Gray

hi def todotxtDone ctermfg=darkgray gui=strikethrough

hi def todotxtOverdueTag ctermfg=DarkRed ctermbg=Black
hi def todotxtContextTag ctermfg=LightBlue ctermbg=Black
hi def todotxtProjectTag ctermfg=Magenta ctermbg=Black
hi def todotxtMetadataEntry ctermfg=DarkBlue ctermbg=Black

let b:current_syntax = "todotxt"
