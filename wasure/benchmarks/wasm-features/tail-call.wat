;; Name: Tail call
;; Proposal: https://github.com/webassembly/tail-call
;; Features: tail_call

(module
  (memory (export "memory") 1)
  (func
    return_call 0
  )
  (func (export "_start") (export "main")
    nop              
  )
)
