(module
  (import "wasi:http/incoming-handler@0.2.0" "handle"
    (func $handle (param i32) (result i32)))

  (func (export "_start")
    (drop (call $handle (i32.const 0))))
)
