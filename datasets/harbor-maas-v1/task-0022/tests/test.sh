#!/bin/bash
mkdir -p /logs/verifier
uvx --with pytest==8.4.1 --with pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/handler_test.go /tests/models_test.go /tests/discovery_test.go /tests/handler_test.go /tests/selector_test.go /tests/cross_namespace_test.go /tests/maasmodelref_controller_test.go /tests/tenant_reconcile_test.go /tests/reconciler_test.go /tests/README.md /tests/maas-model.yaml /tests/prow_run_smoke_test.sh /tests/test_api_keys.py /tests/test_config_tenant.py /tests/test_subscription_list_endpoints.py /tests/test_tenant.py -rA -v
if [ $? -eq 0 ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
exit 0
