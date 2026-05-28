 #   3. Install OpenDataHub (ODH) operator with DataScienceCluster (KServe)
 #   4. Deploy MaaS system (free + premium + e2e test fixtures: LLMIS + MaaSModelRef + MaaSAuthPolicy + MaaSSubscription)
 #   5. Setup test tokens (admin + regular user) for comprehensive testing
#   6. Run E2E tests (API keys + subscription + models + tenant + ...)
 #   7. Run deployment validation + token metadata verification
 # 
 # USAGE:
 #   OIDC_USERNAME - Required when EXTERNAL_OIDC=true; test user for OIDC token requests
 #   OIDC_PASSWORD - Required when EXTERNAL_OIDC=true; password for the OIDC test user
 #   DEPLOYMENT_NAMESPACE - Namespace of MaaS API and controller (default: opendatahub)
#   MAAS_SUBSCRIPTION_NAMESPACE - Namespace of MaaS CRs and Tenant CR (default: models-as-a-service)
#   GATEWAY_NAMESPACE - Namespace for payload-processing deployment checks (default: openshift-ingress)
 #   MODEL_NAMESPACE - Namespace of models and MaaSModelRefs (default: llm)
 #
 # TIMEOUT CONFIGURATION (all in seconds, sourced from deployment-helpers.sh):
     export GATEWAY_HOST="${HOST}"
     export DEPLOYMENT_NAMESPACE
     export MAAS_SUBSCRIPTION_NAMESPACE
    export GATEWAY_NAMESPACE="${GATEWAY_NAMESPACE:-openshift-ingress}"
     # Skip TLS verification in CI (self-signed certs)
     export E2E_SKIP_TLS_VERIFY=true
     # Set MODEL_NAME explicitly - maas-api /v1/models currently only lists MaaSModelRefs
         echo "⚠️  WARNING: Gateway not reachable after ${gw_timeout}s, proceeding anyway (tests may fail)"
     fi
 
    # Run all e2e tests: API keys, namespace scoping, negative security, subscription, models, tenant
     if ! PYTHONPATH="$test_dir:${PYTHONPATH:-}" pytest \
         -v --maxfail=5 --disable-warnings \
         --junitxml="$xml" \
         "$test_dir/tests/test_negative_security.py" \
         "$test_dir/tests/test_subscription.py" \
         "$test_dir/tests/test_models_endpoint.py" \
        "$test_dir/tests/test_external_models.py" \
        "$test_dir/tests/test_tenant.py" \
        "$test_dir/tests/test_config_tenant.py" ; then
         echo "❌ ERROR: E2E tests failed"
         exit 1
     fi