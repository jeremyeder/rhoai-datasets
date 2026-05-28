             # - sa_with_auth: in auth policy (so the policy exists)
             # - sa_with_sub: in subscription but NOT in auth policy
             _ = _create_sa_token(sa_with_auth, namespace=ns)  # SA creation only - token unused
            oc_token_with_sub = _create_sa_token(sa_with_sub, namespace=MODEL_NAMESPACE)  # Different namespace
 
             sa_with_auth_user = _sa_to_user(sa_with_auth, namespace=ns)
            sa_with_sub_user = _sa_to_user(sa_with_sub, namespace=MODEL_NAMESPACE)
 
             # Delete simulator-access so system:authenticated doesn't grant auth
             _delete_cr("maasauthpolicy", SIMULATOR_ACCESS_POLICY)
             _delete_cr("maassubscription", subscription_name, namespace=ns)
             _delete_cr("maasauthpolicy", auth_policy_name, namespace=ns)
             _delete_sa(sa_with_auth, namespace=ns)
            _delete_sa(sa_with_sub, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_e2e_single_subscription_auto_selects(self):
         sa_name = "e2e-status-active-sa"
 
         try:
            _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             _create_test_auth_policy(auth_name, MODEL_REF, users=[sa_user])
             _create_test_subscription(subscription_name, MODEL_REF, users=[sa_user])
         finally:
             _delete_cr("maassubscription", subscription_name, namespace=ns)
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_subscription_failed_status_with_missing_model(self):
         missing_model = "nonexistent-model-xyz"
 
         try:
            _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             # Create subscription with non-existent model
             _create_test_subscription(subscription_name, missing_model, users=[sa_user])
 
         finally:
             _delete_cr("maassubscription", subscription_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_authpolicy_active_status_with_valid_model(self):
         sa_name = "e2e-status-active-auth-sa"
 
         try:
            _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             _create_test_auth_policy(auth_name, MODEL_REF, users=[sa_user])
 
 
         finally:
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_authpolicy_failed_status_with_missing_model(self):
         missing_model = "nonexistent-model-abc"
 
         try:
            _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             # Create auth policy with non-existent model
             _create_test_auth_policy(auth_name, missing_model, users=[sa_user])
 
         finally:
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_subscription_degraded_status_with_partial_models(self):
         missing_model = "nonexistent-model-partial"
 
         try:
            _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             # Create auth policy for valid model only
             _create_test_auth_policy(auth_name, MODEL_REF, users=[sa_user])
         finally:
             _delete_cr("maassubscription", subscription_name, namespace=ns)
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_subscription_degraded_trlp_blocks_inference(self):
 
             # Step 2: Create auth policy and subscription
             log.info("Step 2: Creating subscription with Kuadrant controller down...")
            sa_token = _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             _create_test_auth_policy(auth_name, TRLP_TEST_MODEL_REF, users=[sa_user])
             _create_test_subscription(subscription_name, TRLP_TEST_MODEL_REF, users=[sa_user])
             # Clean up resources (but not the model - it's pre-deployed)
             _delete_cr("maassubscription", subscription_name, namespace=ns)
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_authpolicy_degraded_status_with_partial_models(self):
         missing_model = "nonexistent-model-auth-partial"
 
         try:
            _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             # Create auth policy with both valid and missing models
             _create_test_auth_policy(auth_name, [MODEL_REF, missing_model], users=[sa_user])
 
         finally:
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_subscription_status_transitions_on_model_deletion(self):
         sa_name = "e2e-status-transition-sa"
 
         try:
            _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             # Create a temporary model
             _create_test_maas_model(model_name, llmis_name=MODEL_REF, namespace=MODEL_NAMESPACE)
             _delete_cr("maassubscription", subscription_name, namespace=ns)
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
             _delete_cr("maasmodelref", model_name, namespace=MODEL_NAMESPACE)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
 class TestDegradedSubscriptionFiltering:
         missing_model = "nonexistent-model-inf"
 
         try:
            oc_token = _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             # Create auth policy for valid model only
             _create_test_auth_policy(auth_name, MODEL_REF, users=[sa_user])
         finally:
             _delete_cr("maassubscription", subscription_name, namespace=ns)
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_failed_subscription_blocks_inference(self):
         sa_name = "e2e-failed-sub-inf-sa"
 
         try:
            oc_token = _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             # Create auth policy for valid model
             _create_test_auth_policy(auth_name, MODEL_REF, users=[sa_user])
         finally:
             _delete_cr("maassubscription", subscription_name, namespace=ns)
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_models_endpoint_with_degraded_subscription_api_key(self):
         missing_model = "nonexistent-model-apikey"
 
         try:
            oc_token = _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             # Create auth policy
             _create_test_auth_policy(auth_name, MODEL_REF, users=[sa_user])
         finally:
             _delete_cr("maassubscription", subscription_name, namespace=ns)
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_models_endpoint_with_degraded_subscription_kube_token(self):
         missing_model = "nonexistent-model-kube"
 
         try:
            oc_token = _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             # Create auth policy
             _create_test_auth_policy(auth_name, MODEL_REF, users=[sa_user])
         finally:
             _delete_cr("maassubscription", subscription_name, namespace=ns)
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()