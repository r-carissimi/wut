;; Name: Legacy Exception Handling
;; Proposal: https://github.com/WebAssembly/exception-handling
;; Features: exceptions

(module
  (memory (export "memory") 1)
  (func
    try
    catch_all
    end
  )
  (func (export "_start") (export "main")
    call 0              
  )
)
