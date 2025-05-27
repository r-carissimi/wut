(module
  (memory (export "memory") 1)
  (type (;0;) (func (param i32) (result i32)))
  (type (;1;) (func (param (ref 0)) (result i32)))
  (type (;2;) (func (result i32)))
  (func (;0;) (type 1) (param (ref 0)) (result i32)
    i32.const 10
    i32.const 42
    local.get 0
    call_ref 0
    i32.add
  )
  (func (;1;) (type 0) (param i32) (result i32)
    local.get 0
    i32.const 1
    i32.add
  )
  (func (;2;) (type 2) (result i32)
    ref.func 1
    call 0
  )
  (export "main" (func 2))
  (export "_start" (func 2))
  (elem (;0;) declare func 1)
)