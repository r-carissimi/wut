(module
  (import "wasi_snapshot_preview1" "random_get"
    (func $random_get (param i32 i32) (result i32)))
  (memory 1)
  (export "memory" (memory 0))
  (func (export "_start")
    (i32.const 0)
    (i32.const 4)
    call $random_get
    drop))
