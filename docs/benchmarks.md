# 📈 Resultados dos Benchmarks Quantitativos & Suíte de Testes

Testes E2E executados através do script [`tests/benchmark_skills.py`](../tests/benchmark_skills.py) e suíte unitária em [`tests/unit/`](../tests/unit/), aferindo taxa de compressão real, integridade de parsing, latência de inferência e validação sintática in-memory.

---

## 1. Poda de Tokens por AST (`ast-search`)

Executado em amostras reais de serviços Python e controladores TypeScript:

| Linguagem / Módulo | Tokens Brutos | Tokens Comprimidos | Redução de Tokens | Redução de Caracteres | Redução de Linhas | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Python (`StreamProcessor`)** | 1.218 | 386 | **68.3%** | 72.1% | 71.2% | ✅ PASS |
| **TypeScript (`RouterService`)** | 1.213 | 387 | **68.1%** | 65.6% | 74.1% | ✅ PASS |
| **Média Ponderada** | - | - | **68.2%** | **68.9%** | **72.6%** | ✅ PASS |

> **Validação de Sintaxe:** 100% dos esqueletos de código comprimidos continuam compiláveis e passam no `ast.parse()` sem erros.

---

## 2. Latência do Guardrail In-Memory (`hook_pre_tool.py`)

| Operação | Tempo Medido | Impacto Prático |
| :--- | :---: | :--- |
| **Parse AST em Memória (100 funções)** | **0.26 ms** | Validação sintática instantânea antes de encostar no SSD |
| **Execução Total do Hook PreTool (com spawn)** | **29.7 ms** | Zero percepção de lag para o desenvolvedor |
| **Tokens Poupados por Erro Bloqueado** | **5.000 a 15.000 tokens** | Elimina tracebacks gigantescos de compilação no chat |

---

## 3. Velocidade de Inferência dos Modelos Locais (Apple Silicon M-Series)

| Modelo | Tamanho VRAM | Velocidade Média | Papel no Sistema |
| :--- | :---: | :---: | :--- |
| **`smollm2:1.7b`** | 1.0 GB ativo | **~120-130 tokens/s** | Resolução ultra-rápida de micro-tarefas e tipagem |
| **`deepseek-r1:1.5b`** | 1.1 GB | **~80-95 tokens/s** | Raciocínio cético e extração de JSON |
| **`qwen2.5-coder:3b`** | 1.9 GB | **~65-75 tokens/s** | Funções utilitárias e boilerplate rápido |
| **`qwen2.5-coder:7b`** | 4.7 GB | **~35-40 tokens/s** | Geração e refatoração densa com 0 tokens de nuvem |
| **`nomic-embed-text`** | 274 MB | **<15 ms / embedding** | Vetorização local para RAG semântico no código |

---

## 4. Suíte Automatizada de Testes (55 Testes Unitários & Integração)

O projeto conta com suíte estruturada em [`tests/unit/`](../tests/unit/) e [`tests/integration/`](../tests/integration/) com zero dependências externas:

```
test_read_write_roundtrip (integration.test_adapters.TestLocalFileSystemAdapter) ... ok
test_extract_chunks (integration.test_adapters.TestMultiLanguageAstAdapter) ... ok
test_json_valid_and_invalid (integration.test_adapters.TestMultiLanguageAstAdapter) ... ok
test_python_invalid_syntax (integration.test_adapters.TestMultiLanguageAstAdapter) ... ok
test_python_skeletonize (integration.test_adapters.TestMultiLanguageAstAdapter) ... ok
test_python_valid_syntax (integration.test_adapters.TestMultiLanguageAstAdapter) ... ok
test_clean_code_approved_directly_without_refinement (unit.test_adversarial_reflector.TestAdversarialReflector) ... ok
test_fallback_heuristic_parsing_when_skeptic_not_json (unit.test_adversarial_reflector.TestAdversarialReflector) ... ok
test_flawed_code_intercepted_and_self_refined (unit.test_adversarial_reflector.TestAdversarialReflector) ... ok
test_granular_invalidation_and_virtual_assembly_on_single_method_change (unit.test_ast_merkle_engine.TestAstMerkleEngine) ... ok
test_json_and_typescript_heuristic_decomposition (unit.test_ast_merkle_engine.TestAstMerkleEngine) ... ok
test_l2_sqlite_persistence_roundtrip (unit.test_ast_merkle_engine.TestAstMerkleEngine) ... ok
test_python_decomposition_symbols_and_classes (unit.test_ast_merkle_engine.TestAstMerkleEngine) ... ok
test_zero_modification_yields_100_percent_granular_hits (unit.test_ast_merkle_engine.TestAstMerkleEngine) ... ok
test_empty_steps (unit.test_context_squeezer.TestEpistemicContextSqueezer) ... ok
test_non_destructive_guarantee (unit.test_context_squeezer.TestEpistemicContextSqueezer) ... ok
test_preserves_recent_turns_and_user_input (unit.test_context_squeezer.TestEpistemicContextSqueezer) ... ok
test_respects_token_ceiling (unit.test_context_squeezer.TestEpistemicContextSqueezer) ... ok
test_telemetry_metrics_aggregation (unit.test_context_squeezer.TestEpistemicContextSqueezer) ... ok
test_code_chunk_creation (unit.test_domain.TestDomainEntities) ... ok
test_session_state_to_markdown (unit.test_domain.TestDomainEntities) ... ok
test_cost_usd_conversions (unit.test_domain.TestDomainValueObjects) ... ok
test_diff_patch_validation (unit.test_domain.TestDomainValueObjects) ... ok
test_model_tier_values (unit.test_domain.TestDomainValueObjects) ... ok
test_token_count_negative_raises_value_error (unit.test_domain.TestDomainValueObjects) ... ok
test_token_count_positive_and_conversion (unit.test_domain.TestDomainValueObjects) ... ok
test_memoized_call_arbitrary_function (unit.test_epistemic_cache.TestEpistemicMemoizer) ... ok
test_memoized_skeletonize_cache_hit (unit.test_epistemic_cache.TestEpistemicMemoizer) ... ok
test_invalidation_by_content_hash (unit.test_epistemic_cache.TestSqliteEpistemicCacheAdapter) ... ok
test_l1_and_l2_roundtrip (unit.test_epistemic_cache.TestSqliteEpistemicCacheAdapter) ... ok
test_l2_promotion_on_l1_eviction (unit.test_epistemic_cache.TestSqliteEpistemicCacheAdapter) ... ok
test_micro_task_resolved_by_smollm_successfully (unit.test_hierarchical_cascade.TestHierarchicalCascade) ... ok
test_micro_task_syntax_flaw_silently_promotes_to_7b (unit.test_hierarchical_cascade.TestHierarchicalCascade) ... ok
test_structural_task_routed_directly_to_7b (unit.test_hierarchical_cascade.TestHierarchicalCascade) ... ok
test_build_request_options_injects_keep_alive_and_calibrated_num_keep (unit.test_inference_optimizer.TestInferenceOptimizer) ... ok
test_vram_coresidence_budget_validation (unit.test_inference_optimizer.TestInferenceOptimizer) ... ok
test_telemetry_metrics_accumulation (unit.test_inference_optimizer.TestInferenceOptimizer) ... ok
test_inspect_vram_fallback_and_core_profiles (unit.test_inference_optimizer.TestInferenceOptimizer) ... ok
test_warmup_async_starts_daemon_thread (unit.test_inference_optimizer.TestInferenceOptimizer) ... ok
test_prewarm_file_success (unit.test_pre_warmer.TestPredictivePreWarmer) ... ok
test_prewarm_file_unsupported_extension (unit.test_pre_warmer.TestPredictivePreWarmer) ... ok
test_start_and_stop_lifecycle (unit.test_pre_warmer.TestPredictivePreWarmer) ... ok
test_watcher_detects_file_save_and_prewarms (unit.test_pre_warmer.TestPredictivePreWarmer) ... ok
test_skeletonize_calculates_reduction (unit.test_use_cases.TestCodeSkeletonizer) ... ok
test_classifies_cross_module_prompt_as_system_2 (unit.test_use_cases.TestCognitiveArbiter) ... ok
test_classifies_mechanical_prompt_as_system_1 (unit.test_use_cases.TestCognitiveArbiter) ... ok
test_token_budget_calculation (unit.test_use_cases.TestCognitiveArbiter) ... ok
test_allows_retry_on_first_failure (unit.test_use_cases.TestEscalationCircuitBreaker) ... ok
test_trips_on_second_failure_and_synthesizes_handoff (unit.test_use_cases.TestEscalationCircuitBreaker) ... ok
test_blocks_dangerous_commands (unit.test_use_cases.TestGuardrailInterceptor) ... ok
test_blocks_unsliced_view_file_on_long_files (unit.test_use_cases.TestGuardrailInterceptor) ... ok
test_denies_invalid_syntax_on_replace_file (unit.test_use_cases.TestGuardrailInterceptor) ... ok
test_wraps_test_commands_with_test_slicer (unit.test_use_cases.TestGuardrailInterceptor) ... ok
test_wraps_verbose_commands_with_rtk (unit.test_use_cases.TestGuardrailInterceptor) ... ok
test_draft_success_on_first_try (unit.test_use_cases.TestSpeculativeDrafter) ... ok
----------------------------------------------------------------------
Ran 55 tests in 0.332s - OK (100% PASS)
```

---

## 5. Como Reproduzir os Benchmarks

### Executar a suíte completa de testes unitários e integração:
```bash
python3 -m unittest discover -s tests -v
```

### Executar o benchmark E2E de redução quantitativa de tokens (25 asserções):
```bash
python3 tests/benchmark_skills.py
```
