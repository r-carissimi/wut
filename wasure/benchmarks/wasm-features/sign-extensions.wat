;; Name: Sign-extension operators
;; Proposal: https://github.com/WebAssembly/sign-extension-ops

(module
  (memory (export "memory") 1)
  (func
    i32.const 0
    i32.extend8_s
    drop
  )
  (func (export "_start") (export "main")
    call 0              
  )
)
