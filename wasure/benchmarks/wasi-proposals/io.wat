(module
  (import "wasi_snapshot_preview1" "fd_write"
    (func $fd_write (param i32 i32 i32 i32) (result i32)))
  (memory 1)
  (export "memory" (memory 0))
  (func (export "_start")
    (i32.const 1) ;; fd = stdout
    (i32.const 0) ;; iovs
    (i32.const 1) ;; iovs_len
    (i32.const 20) ;; nwritten
    call $fd_write
    drop))
