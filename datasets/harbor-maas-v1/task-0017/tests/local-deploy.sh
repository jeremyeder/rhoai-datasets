   ok "MaaS CRDs already installed"
 else
   kubectl apply -f "$PROJECT_ROOT/deployment/base/maas-controller/crd/bases/"
  for crd in configs.maas.opendatahub.io tenants.maas.opendatahub.io \
             externalmodels.maas.opendatahub.io maasmodelrefs.maas.opendatahub.io \
              maassubscriptions.maas.opendatahub.io maasauthpolicies.maas.opendatahub.io; do
     kubectl wait --for=condition=Established "crd/$crd" --timeout=60s
   done
 
 step "Deploying test fixtures"
 
LLM_KATAN_FQDN="${LLM_KATAN_FQDN:-3-147-232-199.sslip.io}"
 MODEL_NAMESPACE="llm"
 INTERNAL_MODEL_NAMESPACE="llm-internal"
 