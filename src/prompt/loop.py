LOOP_MERGING_DESC = \
"""

Loop merging strategy

Concept:
Loop merging is a high-level synthesis (HLS) optimization technique that combines multiple loops sharing the **same iteration bounds** into a single loop. This reduces loop control overhead, improves pipeline initiation intervals (II), and enhances resource sharing potential. It is particularly effective for memory-bound kernels with independent computation patterns.

Apply Scenario:
- Apply this strategy only if the loops:
  - Have identical or compatible loop bounds (same loop variable, range, and step);
  - Do not have inter-loop data dependencies (i.e., the output of one loop is not used in the next loop);
  - Operate on different arrays or disjoint memory regions (no read/write conflicts);
  - Have a similar loop nesting level and structure.

Apply Rule:
- If multiple loops iterate over the same range or bounds, try to combine them into a single loop.
- Ensure that the logic from all loops is preserved and executed in order or safely parallel.
- The merged loop should preserve functional correctness while improving latency and resource sharing.
- Prefer merging loops that operate on independent arrays or different operations over the same index.

Example:
```cpp
// Before optimization:
for (int i = 0; i < 100; ++i)
    A[i] = B[i] + 1;

for (int i = 0; i < 100; ++i)
    C[i] = D[i] * 2;

for (int i = 0; i < 100; ++i)
    E[i] = F[i] - 3;

// After optimization:
for (int i = 0; i < 100; ++i) {
    A[i] = B[i] + 1;
    C[i] = D[i] * 2;
    E[i] = F[i] - 3;
}
```
"""

LOOP_INTERCHANGE_DESC = \
"""

Loop interchange strategy

Concept:
Loop interchange is a high-level synthesis (HLS) optimization technique that exchanges the order of nested loops to improve memory access patterns, pipeline efficiency, and parallelism. By adjusting the loop hierarchy, it can reduce memory access strides, enhance spatial/temporal locality, and improve performance on array-based computations.

Apply Scenario:
- Apply this strategy if:
  - You have **nested loops** (e.g., 2D or 3D loops);
  - The inner loop accesses memory with non-unit stride, causing inefficient memory access or poor cache usage;
  - The outer loop is small (e.g., 4–10 iterations) and the inner loop is large (e.g., 100+), and switching them would benefit pipelining or locality;
  - The loop order is not constrained by data dependencies (i.e., loop-carried dependencies do not prevent reordering).

Apply Rule:
- Interchange loops to make memory access patterns more efficient (e.g., access arrays row-wise instead of column-wise);
- Prefer interchanging loops so that the **innermost loop accesses contiguous memory addresses**;
- Ensure that changing the order of loops **does not violate data dependencies or affect correctness**;
- After interchange, consider applying `#pragma HLS pipeline` to the innermost loop for better performance.

Example:
```cpp
// Before optimization (poor memory access pattern for row-major arrays):
for (int j = 0; j < N; ++j) {
    for (int i = 0; i < M; ++i) {
        A[i][j] += 1;
    }
}

// After optimization (better spatial locality in row-major layout):
for (int i = 0; i < M; ++i) {
    for (int j = 0; j < N; ++j) {
        A[i][j] += 1;
    }
}
```
"""

LOOP_TILING_DESC = \
"""

Loop tiling strategy

Concept:
Loop tiling is a high-level synthesis (HLS) optimization technique that divides the iteration space of a loop into smaller blocks or "tiles". This improves temporal and spatial data locality, reduces cache misses, enhances BRAM reuse, and enables more efficient pipelining and parallelization. It is especially effective for memory-bound nested loops such as matrix operations or stencil computations.

Apply Scenario:
- Apply this strategy when:
  - The code contains **nested loops** (usually 2 or more dimensions);
  - The algorithm accesses large arrays with regular patterns;
  - Memory bandwidth or on-chip buffer reuse is a performance bottleneck;
  - You want to enable partial unrolling or pipelining within tiles;
  - The computation fits into smaller working sets (e.g., BRAM or local buffers).

Apply Rule:
- Split each loop into two: an **outer tile loop** and an **inner local loop**;
- The outer loop iterates over tiles, and the inner loop iterates within the tile;
- Choose tile sizes carefully to match on-chip memory size and loop bounds;
- Apply `#pragma HLS pipeline` to the inner loop, and `#pragma HLS dataflow` to tile-level stages if independent;
- Ensure boundary handling logic if loop bounds are not divisible by tile size.

Example:
```cpp
// Before optimization:
for (int i = 0; i < N; ++i)
    for (int j = 0; j < M; ++j)
        A[i][j] += B[i][j];

// After optimization with tile size Ti x Tj:
for (int ii = 0; ii < N; ii += Ti)
    for (int jj = 0; jj < M; jj += Tj)
        for (int i = ii; i < ii + Ti && i < N; ++i)
            for (int j = jj; j < jj + Tj && j < M; ++j)
                A[i][j] += B[i][j];
```
"""
