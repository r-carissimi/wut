;; Name: Reference Types
;; Proposal: https://github.com/WebAssembly/reference-types

(module
  (func
    ref.null func
    drop
  )
  (func (export "_start") 
    call 0              
  )
)
