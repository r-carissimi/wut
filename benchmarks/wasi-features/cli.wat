(module
  (import "wasi_snapshot_preview1" "args_get"
    (func $args_get (param i32 i32) (result i32)))
  (memory 1)
  (export "memory" (memory 0))
  (func (export "_start")
    (i32.const 0)
    (i32.const 8)
    call $args_get
    drop))
