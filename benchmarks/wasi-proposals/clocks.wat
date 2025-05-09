(module
  (import "wasi_snapshot_preview1" "clock_time_get"
    (func $clock_time_get (param i32 i64 i32) (result i32)))
  (memory 1)
  (export "memory" (memory 0))
  (func (export "_start")
    (i32.const 0) ;; CLOCK_REALTIME
    (i64.const 0)
    (i32.const 8)
    call $clock_time_get
    drop))
