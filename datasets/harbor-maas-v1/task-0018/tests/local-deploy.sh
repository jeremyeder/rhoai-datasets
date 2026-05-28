   ok "MaaS CRDs already installed"
 else
   kubectl apply -f "$PROJECT_ROOT/deployment/base/maas-controller/crd/bases/"
  for crd in configs.maas.opendatahub.io tenants.maas.opendatahub.io \
             externalmodels.maas.opendatahub.io maasmodelrefs.maas.opendatahub.io \
              maassubscriptions.maas.opendatahub.io maasauthpolicies.maas.opendatahub.io; do
     kubectl wait --for=condition=Established "crd/$crd" --timeout=60s
   done