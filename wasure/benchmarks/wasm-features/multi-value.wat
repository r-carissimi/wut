;; Name: Multi-value
;; Proposal: https://github.com/WebAssembly/multi-value
;; Features: multi_value

(module
  (memory (export "memory") 1)
  (func (result i32 i32)
    i32.const 0
    i32.const 0
  )
  (func (export "_start") (export "main")
    call 0
    drop
    drop              
  )
)
