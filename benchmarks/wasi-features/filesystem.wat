(module
  (import "wasi_snapshot_preview1" "path_open"
    (func $path_open
      (param i32 i32 i32 i32 i32 i64 i64 i32 i32) (result i32)))
  (memory 1)
  (export "memory" (memory 0))
  (data (i32.const 8) ".") ;; path buffer
  (func (export "_start")
    (i32.const 3) ;; fd (preopened directory)
    (i32.const 0) ;; dirflags
    (i32.const 8) ;; path ptr
    (i32.const 1) ;; path len
    (i32.const 0) ;; oflags
    (i64.const 0) ;; rights_base
    (i64.const 0) ;; rights_inheriting
    (i32.const 0) ;; fdflags
    (i32.const 20) ;; fd_out
    call $path_open
    drop))
