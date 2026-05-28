     kubectl get tokenratelimitpolicies -A 2>/dev/null || true
     echo ""
     echo "--- MaaS CRs ---"
    kubectl get configs.maas.opendatahub.io -o wide 2>/dev/null || true
     kubectl get maasmodelrefs -n "$DEPLOYMENT_NAMESPACE" 2>/dev/null || true
     kubectl get maasauthpolicies,maassubscriptions -n "$MAAS_SUBSCRIPTION_NAMESPACE" 2>/dev/null || true
     kubectl get tenants -n "$MAAS_SUBSCRIPTION_NAMESPACE" 2>/dev/null || true