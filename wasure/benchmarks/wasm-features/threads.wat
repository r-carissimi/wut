;; Name: Threads
;; Proposal: https://github.com/webassembly/threads
;; Features: threads

(module
  (memory (export "memory") 1 1 shared)
  (func
    i32.const 0
    i32.atomic.load
    drop
  )
  (func (export "_start") (export "main")
    call 0              
  )
)
