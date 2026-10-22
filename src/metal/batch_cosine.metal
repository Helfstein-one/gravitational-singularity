#include <metal_stdlib>
using namespace metal;

// Metal Shading Language (MSL) Compute Kernel for Batch Cosine Similarity
// Dispatches 5,000+ AST vector embeddings in a single GPU command buffer.
kernel void batch_cosine_similarity(
    device const float* query       [[buffer(0)]],
    device const float* candidates  [[buffer(1)]],
    device float* results           [[buffer(2)]],
    constant uint& dimension        [[buffer(3)]],
    uint id                         [[thread_position_in_grid]])
{
    float dot = 0.0f;
    float norm_q = 0.0f;
    float norm_c = 0.0f;

    uint offset = id * dimension;

    // SIMD vector unrolling for 768-dim embedding coordinates
    for (uint i = 0; i < dimension; ++i) {
        float q = query[i];
        float c = candidates[offset + i];
        dot += q * c;
        norm_q += q * q;
        norm_c += c * c;
    }

    float denom = sqrt(norm_q) * sqrt(norm_c);
    results[id] = (denom > 1e-7f) ? (dot / denom) : 0.0f;
}
