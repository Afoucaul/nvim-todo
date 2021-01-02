if exists("b:current_syntax")
    finish
endif

hi def todoDone ctermfg=darkgray

hi def priorityA ctermfg=darkred
hi def priorityB ctermfg=yellow
hi def priorityC ctermfg=green

syntax match priorityA "\v^(x )?\s*\(A\).*$"
syntax match priorityB "\v^(x )?\s*\(B\).*$"
syntax match priorityC "\v^(x )?\s*\(C\).*$"

syntax match todoDone "\vx.*$"

echom "Set colors"

let b:current_syntax = "todotxt"
