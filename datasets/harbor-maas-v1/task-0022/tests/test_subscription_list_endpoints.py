     SIMULATOR_SUBSCRIPTION,
     TIMEOUT,
     TLS_VERIFY,
    _apply_cr,
     _create_api_key,
     _create_sa_token,
     _create_test_auth_policy,
     for ref in sub["model_refs"]:
         assert "name" in ref, f"model_ref missing name: {ref}"
         assert isinstance(ref["name"], str), "model_ref name must be string"
        # display_name and description are optional (omitempty) but must be strings when present
        if "display_name" in ref:
            assert isinstance(ref["display_name"], str), \
                f"model_ref display_name must be string, got {type(ref['display_name'])}: {ref}"
        if "description" in ref:
            assert isinstance(ref["description"], str), \
                f"model_ref description must be string, got {type(ref['description'])}: {ref}"

    # Optional subscription-level fields
     if "display_name" in sub:
         assert isinstance(sub["display_name"], str), "display_name must be string"
     if "organization_id" in sub:
             _delete_sa(sa_name, namespace=sa_ns)
 
 
    def test_model_ref_display_name_and_description_enriched(self):
        """Model refs include display_name and description from MaaSModelRef annotations."""
        sa_name = "e2e-enrichment-sa"
        sa_ns = "default"
        maas_ns = _ns()
        model_ref_name = "e2e-enrichment-model-ref"
        model_ns = MODEL_NAMESPACE
        subscription_name = "e2e-enrichment-sub"
        expected_display_name = "E2E Enrichment Test Model"
        expected_description = "Model created by e2e test to verify display_name/description enrichment"

        try:
            sa_token = _create_sa_token(sa_name, namespace=sa_ns)
            sa_user = _sa_to_user(sa_name, namespace=sa_ns)

            # Create a MaaSModelRef with display-name and description annotations.
            # Points to the existing e2e-distinct-simulated LLMIS so the controller
            # can reconcile the subscription to Active.
            _apply_cr({
                "apiVersion": "maas.opendatahub.io/v1alpha1",
                "kind": "MaaSModelRef",
                "metadata": {
                    "name": model_ref_name,
                    "namespace": model_ns,
                    "annotations": {
                        "openshift.io/display-name": expected_display_name,
                        "openshift.io/description": expected_description,
                    },
                },
                "spec": {
                    "modelRef": {
                        "kind": "LLMInferenceService",
                        "name": "e2e-distinct-simulated",
                    }
                },
            })

            _create_test_subscription(
                subscription_name,
                model_ref_name,
                users=[sa_user],
            )

            api_key = _create_api_key(sa_token, name=f"{sa_name}-key")
            _wait_reconcile()

            url = f"{_maas_api_url()}/v1/subscriptions"
            r = requests.get(
                url,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=TIMEOUT,
                verify=TLS_VERIFY,
            )

            assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
            data = r.json()

            test_sub = next(
                (s for s in data if s["subscription_id_header"] == subscription_name),
                None,
            )
            assert test_sub is not None, \
                f"Subscription '{subscription_name}' not found in {[s['subscription_id_header'] for s in data]}"

            refs = test_sub.get("model_refs", [])
            assert len(refs) >= 1, "Expected at least 1 model_ref"

            enriched_ref = next((r for r in refs if r["name"] == model_ref_name), None)
            assert enriched_ref is not None, \
                f"model_ref '{model_ref_name}' not found in model_refs: {refs}"

            assert enriched_ref.get("display_name") == expected_display_name, (
                f"Expected display_name={expected_display_name!r}, "
                f"got {enriched_ref.get('display_name')!r}"
            )
            assert enriched_ref.get("description") == expected_description, (
                f"Expected description={expected_description!r}, "
                f"got {enriched_ref.get('description')!r}"
            )

            log.info(
                "Model ref '%s' enriched with display_name=%r description=%r",
                model_ref_name, enriched_ref.get("display_name"), enriched_ref.get("description"),
            )

        finally:
            _delete_cr("maassubscription", subscription_name, namespace=maas_ns)
            _delete_cr("maasmodelref", model_ref_name, namespace=model_ns)
            _delete_sa(sa_name, namespace=sa_ns)


 class TestListSubscriptionsForModel:
     """E2E tests for GET /v1/model/:model-id/subscriptions."""
 