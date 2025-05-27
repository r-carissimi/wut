;; Name: Relaxed SIMD
;; Proposal: https://github.com/webassembly/relaxed-simd
;; Features: relaxed_simd

(module
  (memory (export "memory") 1)
  (func (result v128)
    i32.const 1
    i8x16.splat
    i32.const 2
    i8x16.splat
    i8x16.relaxed_swizzle
  )
  (func (export "_start") (export "main")
    call 0
    drop              
  )
)
