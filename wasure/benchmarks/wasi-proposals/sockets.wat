(module
  (import "wasi_snapshot_preview1" "sock_connect"
    (func $sock_connect (param i32 i32 i32) (result i32)))
  (memory 1)
  (func (export "_start")
    (i32.const 0) ;; dummy sockfd
    (i32.const 0) ;; dummy addr_ptr
    (i32.const 0) ;; dummy addr_len
    call $sock_connect
    drop)
)
