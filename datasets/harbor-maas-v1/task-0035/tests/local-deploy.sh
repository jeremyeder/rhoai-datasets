   # Install vanilla KServe (provides base controller, CRDs, webhooks)
   "$PROJECT_ROOT/scripts/installers/install-kserve.sh"
 
  # Scale down kserve-controller-manager — the opendatahub fork image watches
  # Route.route.openshift.io for InferenceGraph, which crash-loops on non-OpenShift
  # clusters. We only need LLMInferenceService, handled by llmisvc-controller-manager.
  kubectl scale deployment/kserve-controller-manager --replicas=0 -n kserve
  ok "KServe installed (main controller scaled to 0 — llmisvc-controller handles LLMInferenceService)"
 fi
 
 # LLMInferenceService controller — separate binary in the opendatahub kserve fork