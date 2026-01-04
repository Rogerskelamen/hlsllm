STATIC_INTERN_ARRAY = \
"""

Static Internal Array Canonicalization

Description:
Convert eligible *purely internal* function-local arrays into static storage to make memory lifetime explicit and hardware-like.
This transformation must preserve not only algorithmic behavior, but also the input/output temporal semantics of the kernel.
This avoids runtime initialization overhead and allows the memory to be initialized directly in the bitstream.
This is a structural canonicalization step, not a performance optimization.

Applicable Scenarios:
- The array is declared inside the function AND is NOT a kernel interface argument.
- The array does NOT alias, shadow, or mirror any kernel parameter array.
- The array size is compile-time constant.
- The function is not invoked concurrently (e.g., not replicated in a dataflow region).
- The array does not need to be reset on each function call.
Do not apply if the array represents per-transaction temporary state.

How to Apply:
- Add the `static` keyword to eligible array declaration.
- Do not change array size, element type, or access pattern.
- Do not introduce new initialization to reset logic.
- Preserve functional behavior exactly.

Example:
```
// before
void filter(int in[256], int out[256]) {
    static int buf[256];
    for (int i = 0; i < 256; i++) {
        buf[i] = in[i];
        out[i] = buf[i] * 2;
    }
}
// after
void filter(int in[256], int out[256]) {
    static int buf[256];
    for (int i = 0; i < 256; i++) {
        buf[i] = in[i];
        out[i] = buf[i] * 2;
    }
}
```
"""

HLS_INTRINSIC_FUNCTION = \
"""

HLS Intrinsic Function Replacement

Description:
Replace manually implemented logic with equivalent HLS-provided intrinsic functions in order to make hardware intent explicit and improve synthesis predictability.
This transformation is purely structural and must not change algorithmic behavior.

Applicable Scenarios:
- Manual logic implements standard math operations such as absolute value, minimum, or maximum.
- FIFO-like or producer–consumer behavior is implemented using arrays and explicit read/write indices.
- A semantically equivalent HLS intrinsic function exists (e.g., hls::abs, hls::min, hls::max, hls::stream).

How to Apply:
- Replace manual math logic with the corresponding HLS math intrinsic.
- Replace FIFO-style array/index-based buffering with hls::stream where semantics match.
- Preserve original data types and control behavior.
- Do not introduce pragmas, additional buffering, or algorithmic changes.

Example:
Math intrinsic replacement

```c
// Before
int diff = (x > y) ? (x - y) : (y - x);

// After
#include "hls_math.h"
int diff = hls::abs(x - y);
```

Supported Intrinsic Categories:
Trigonometric: acos, asin, atan, sin, cos, tan
Hyperbolic: acosh, asinh, atanh, sinh, cosh, tanh
Exponential: exp, exp10, exp2
Logarithmic: ilogb, log, log10, log1p
Power: cbrt, hypot, pow, sqrt
Rounding: ceil, floor, round
Other: abs, divide, fabs
"""

CONTROL_FLOW_CANONICAL = \
"""

Control-Flow Canonicalization

Description:
Rewrite irregular or complex control flow into a structured, single-exit form to improve FSM generation and synthesis stability.
This transformation simplifies control logic without altering functional behavior.

Applicable Scenarios:
- Functions contain early return statements.
- Nested if-else structures complicate control flow.
- Variable assignments depend on control-path exits.
Do not apply if the original control flow is already simple and structured.

How to Apply:
- Replace early returns with condition masks.
- Ensure all outputs are assigned along all control paths.
- Use explicit boolean conditions to guard assignments.
- Preserve execution order and semantics.

Example:
```
// Before
int foo(int a, int b) {
    if (a > 0) {
        if (b > 0)
            return a + b;
    }
    return 0;
}
// After
int foo(int a, int b) {
    bool valid = (a > 0) && (b > 0);
    int result = 0;
    if (valid)
        result = a + b;
    return result;
}
```
"""

MEMORY_ACCESS_LINEAR = \
"""

Memory Access Linearization

Description:
Convert multi-dimensional or computed-index memory accesses into explicit linearized addressing.
This makes memory access patterns more predictable and synthesis-friendly.

Applicable Scenarios:
- Multi-dimensional arrays are accessed inside loops.
- Index expressions involve arithmetic or helper functions.
- Address computation obscures access regularity.
Do not apply if memory accesses are already linear and explicit.

How to Apply:
- Introduce explicit linear index variables.
- Use compile-time constants for stride calculation.
- Preserve the original memory layout and access semantics.
- Do not change loop structure or iteration order.

Example:
```
// Before
int A[64][64];
int val = A[i][j];
// After
int A[64][64];
int idx = i * 64 + j;
int val = ((int*)A)[idx];

// Before
int val = A[f(i)][g(j)];
// After
int row = f(i);
int col = g(j);
int idx = row * W + col;
int val = A_flat[idx];
```
"""
