             oc_token = _create_sa_token(sa_name, namespace=ns)
             sa_user = _sa_to_user(sa_name, namespace=ns)
 
            # Create model and governance resources together so the model
            # can reach Ready (requires MaaSSubscription + MaaSAuthPolicy).
             _create_test_maas_model(model_ref)
             _create_test_auth_policy(auth_policy_name, model_ref, users=[sa_user])
             _create_test_subscription(subscription_name, model_ref, users=[sa_user])
 
            endpoint = _wait_for_maas_model_ready(model_ref, timeout=120)

            # Extract path from endpoint (e.g., https://maas.../llm/facebook-opt-125m-simulated -> /llm/facebook-opt-125m-simulated)
            model_path = urlparse(endpoint).path
 
             # API key bound to this subscription at mint (inference does not send x-maas-subscription)
             api_key = _create_api_key(