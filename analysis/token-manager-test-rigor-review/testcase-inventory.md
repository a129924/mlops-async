# TokenManager TestCase Inventory

| case_id | file_path | test_name | covers_area |
| --- | --- | --- | --- |
| TM-001 | tests/unit/core/test_token_manager.py | test_token_manager_reuses_non_expired_token_without_fetch_or_refresh | token reuse / no fetch-refresh |
| TM-002 | tests/unit/core/test_token_manager.py | test_token_manager_fetches_when_storage_is_empty | empty storage fetch path |
| TM-003 | tests/unit/core/test_token_manager.py | test_token_manager_treats_default_skew_window_as_expired_and_refreshes | default skew refresh path |
| TM-004 | tests/unit/core/test_token_manager.py | test_token_manager_refreshes_once_for_ten_concurrent_waiters | refresh concurrency de-dup |
| TM-005 | tests/unit/core/test_token_manager.py | test_token_manager_translates_refresh_failure_preserving_previous_token | refresh failure translation + state preservation |
| TM-006 | tests/unit/core/test_token_manager.py | test_token_manager_uses_fallback_message_for_empty_generic_fetch_failure | generic exception fallback message |
| TM-007 | tests/unit/core/test_token_manager.py | test_token_manager_preserves_previous_token_state_on_refresh_cancellation | cancellation state preservation |
| TS-001 | tests/unit/core/test_token_storage.py | test_access_token_rejects_naive_expires_at | timezone-aware expires_at validation |
| TS-002 | tests/unit/core/test_token_storage.py | test_access_token_rejects_naive_now_argument | timezone-aware now validation |
| TS-003 | tests/unit/core/test_token_storage.py | test_access_token_is_expired_with_default_60_second_skew | default skew expiry rule |
| TS-004 | tests/unit/core/test_token_storage.py | test_access_token_respects_explicit_skew_override | explicit skew override behavior |
| TS-005 | tests/unit/core/test_token_storage.py | test_in_memory_token_storage_round_trips_and_clears_token_state | token storage set/get/clear |
| AP-001 | tests/unit/core/test_auth_provider.py | test_auth_provider_turns_token_manager_output_into_bearer_header | auth header composition |
| AC-001 | tests/unit/core/test_auth_contract.py | test_internal_auth_contracts_are_not_promoted_to_package_root | package root exposure contract |
| AC-002 | tests/unit/core/test_auth_contract.py | test_token_manager_surface_is_async_and_returns_access_token | token manager async surface contract |
| AC-003 | tests/unit/core/test_auth_contract.py | test_auth_provider_surface_is_async_and_returns_header_mapping | auth provider async surface contract |
| AC-004 | tests/unit/core/test_auth_contract.py | test_token_fetcher_contract_supports_fetch_and_refresh_paths | token fetcher protocol contract |
