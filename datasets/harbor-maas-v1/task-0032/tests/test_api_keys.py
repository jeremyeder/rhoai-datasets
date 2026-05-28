         sa_name = "e2e-apikey-active-sa"
 
         try:
            oc_token = _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             _create_test_auth_policy(auth_name, MODEL_REF, users=[sa_user])
             _create_test_subscription(subscription_name, MODEL_REF, users=[sa_user])
         finally:
             _delete_cr("maassubscription", subscription_name, namespace=ns)
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_create_key_for_degraded_subscription(self):
         missing_model = "nonexistent-model-apikey"
 
         try:
            oc_token = _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             _create_test_auth_policy(auth_name, MODEL_REF, users=[sa_user])
             # Create with valid + missing model to trigger Degraded phase
         finally:
             _delete_cr("maassubscription", subscription_name, namespace=ns)
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_create_key_for_failed_subscription(self):
         sa_name = "e2e-apikey-failed-sa"
 
         try:
            oc_token = _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             _create_test_auth_policy(auth_name, MODEL_REF, users=[sa_user])
             _create_test_subscription(subscription_name, MODEL_REF, users=[sa_user])
         finally:
             _delete_cr("maassubscription", subscription_name, namespace=ns)
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_create_key_for_pending_subscription(self):
         sa_name = "e2e-apikey-pending-sa"
 
         try:
            oc_token = _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             _create_test_auth_policy(auth_name, MODEL_REF, users=[sa_user])
             _create_test_subscription(subscription_name, MODEL_REF, users=[sa_user])
         finally:
             _delete_cr("maassubscription", subscription_name, namespace=ns)
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()
 
     def test_reject_key_for_unreconciled_subscription(self):
             # Scale down controller to prevent reconciliation
             _scale_controller_down()
 
            oc_token = _create_sa_token(sa_name, namespace=MODEL_NAMESPACE)
            sa_user = _sa_to_user(sa_name, namespace=MODEL_NAMESPACE)
 
             _create_test_auth_policy(auth_name, MODEL_REF, users=[sa_user])
             # Create subscription (won't reconcile with controller scaled down)
             _scale_controller_up()
             _delete_cr("maassubscription", subscription_name, namespace=ns)
             _delete_cr("maasauthpolicy", auth_name, namespace=ns)
            _delete_sa(sa_name, namespace=MODEL_NAMESPACE)
             _wait_reconcile()