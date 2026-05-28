             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
             _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()


class TestAPIKeySubscriptionFilter:
    """Tests for POST /api-keys/search subscription filter.

    Verifies that the subscription filter scopes search results to keys
    bound to a specific subscription, and that omitting it returns all keys.
    """

    def test_search_filters_by_subscription(self, api_keys_base_url: str, headers: dict):
        """Search with subscription filter returns only keys bound to that subscription."""
        sub_a = f"e2e-filter-sub-a-{os.urandom(4).hex()}"
        sub_b = f"e2e-filter-sub-b-{os.urandom(4).hex()}"
        ns = _ns()
        sa_name = f"e2e-filter-sa-{os.urandom(4).hex()}"

        key_ids_a = []
        key_ids_b = []
        try:
            # Create one SA authorized for both subscriptions so that
            # exclusion in search results is attributable to the subscription
            # filter, not user-scoping.
            oc_token = _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
            sa_headers = {"Authorization": f"Bearer {oc_token}", "Content-Type": "application/json"}

            _create_test_auth_policy(f"{sub_a}-auth", MODEL_REF, users=[sa_user])
            _create_test_subscription(sub_a, MODEL_REF, users=[sa_user])
            _wait_for_maas_subscription_phase(sub_a, namespace=ns)

            _create_test_auth_policy(f"{sub_b}-auth", MODEL_REF, users=[sa_user])
            _create_test_subscription(sub_b, MODEL_REF, users=[sa_user])
            _wait_for_maas_subscription_phase(sub_b, namespace=ns)

            # Create 2 keys bound to sub_a
            for i in range(2):
                r = requests.post(
                    api_keys_base_url,
                    headers=sa_headers,
                    json={"name": f"e2e-filter-a-{i}", "subscription": sub_a},
                    timeout=TIMEOUT,
                    verify=TLS_VERIFY,
                )
                assert r.status_code in (200, 201), f"Failed to create key for {sub_a}: {r.text}"
                key_ids_a.append(r.json()["id"])

            # Create 1 key bound to sub_b
            r_b = requests.post(
                api_keys_base_url,
                headers=sa_headers,
                json={"name": "e2e-filter-b-0", "subscription": sub_b},
                timeout=TIMEOUT,
                verify=TLS_VERIFY,
            )
            assert r_b.status_code in (200, 201), f"Failed to create key for {sub_b}: {r_b.text}"
            key_ids_b.append(r_b.json()["id"])

            # Search with subscription filter for sub_b — same principal
            r_search = requests.post(
                f"{api_keys_base_url}/search",
                headers=sa_headers,
                json={
                    "filters": {"status": ["active"], "subscription": sub_b},
                    "pagination": {"limit": 50, "offset": 0},
                },
                timeout=TIMEOUT,
                verify=TLS_VERIFY,
            )
            assert r_search.status_code == 200, f"Search failed: {r_search.status_code} {r_search.text}"
            items = r_search.json().get("items") or r_search.json().get("data") or []
            result_ids = [item["id"] for item in items]

            # sub_b key should be present
            for kid in key_ids_b:
                assert kid in result_ids, (
                    f"Key {kid} (subscription={sub_b}) should appear in filtered results"
                )

            # sub_a keys should NOT be present — since the same user owns
            # both, exclusion proves the subscription filter works.
            for kid in key_ids_a:
                assert kid not in result_ids, (
                    f"Key {kid} (subscription={sub_a}) should NOT appear when filtering by {sub_b}"
                )

            log.info("subscription filter correctly scoped search results")

        finally:
            for kid in key_ids_a + key_ids_b:
                requests.delete(f"{api_keys_base_url}/{kid}", headers=sa_headers, timeout=TIMEOUT, verify=TLS_VERIFY)
            _delete_cr("maassubscription", sub_b, namespace=ns)
            _delete_cr("maasauthpolicy", f"{sub_b}-auth", namespace=ns)
            _delete_cr("maassubscription", sub_a, namespace=ns)
            _delete_cr("maasauthpolicy", f"{sub_a}-auth", namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
            _wait_reconcile()

    def test_search_without_subscription_returns_all(self, api_keys_base_url: str, headers: dict):
        """Search without subscription filter returns keys across all subscriptions."""
        key_ids = []
        try:
            # Create keys with explicit subscription binding
            for i in range(2):
                r = requests.post(
                    api_keys_base_url,
                    headers=headers,
                    json={"name": f"e2e-nofilter-{i}", "subscription": SIMULATOR_SUBSCRIPTION},
                    timeout=TIMEOUT,
                    verify=TLS_VERIFY,
                )
                assert r.status_code in (200, 201), f"Failed to create key: {r.text}"
                key_ids.append(r.json()["id"])

            # Search without subscription filter
            r_search = requests.post(
                f"{api_keys_base_url}/search",
                headers=headers,
                json={
                    "filters": {"status": ["active"]},
                    "pagination": {"limit": 50, "offset": 0},
                },
                timeout=TIMEOUT,
                verify=TLS_VERIFY,
            )
            assert r_search.status_code == 200, f"Search failed: {r_search.status_code} {r_search.text}"
            items = r_search.json().get("items") or r_search.json().get("data") or []
            result_ids = [item["id"] for item in items]

            for kid in key_ids:
                assert kid in result_ids, (
                    f"Key {kid} should appear in unfiltered search results"
                )

            log.info("unfiltered search returns all keys (no regression)")

        finally:
            for kid in key_ids:
                requests.delete(f"{api_keys_base_url}/{kid}", headers=headers, timeout=TIMEOUT, verify=TLS_VERIFY)