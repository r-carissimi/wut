;; Name: Legacy Exception Handling
;; Proposal: https://github.com/WebAssembly/exception-handling
;; Features: exceptions

(module
  (func
    try
    catch_all
    end
  )
  (func (export "_start") 
    call 0              
  )
)
