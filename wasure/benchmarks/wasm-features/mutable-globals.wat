;; Name: Importable/Exportable mutable globals

(module
  (global (export "a") (mut i32) (i32.const 0))
  (func (export "_start") 
    nop             
  )
)
