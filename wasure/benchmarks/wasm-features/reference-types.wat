;; Name: Reference Types
;; Proposal: https://github.com/WebAssembly/reference-types

(module
  (memory (export "memory") 1)
  (func
    ref.null func
    drop
  )
  (func (export "_start") (export "main")
    call 0              
  )
)
