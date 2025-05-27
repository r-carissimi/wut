;; Name: Importable/Exportable mutable globals

(module
  (memory (export "memory") 1)
  (global (export "a") (mut i32) (i32.const 0))
  (func (export "_start") (export "main")
    nop             
  )
)
