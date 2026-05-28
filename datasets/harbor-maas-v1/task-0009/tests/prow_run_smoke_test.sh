     fi
     echo "✅ Simulator models ready"
 
    # Wait for governed MaaSModelRefs to transition to Ready phase.
    # Only models with MaaSSubscription + MaaSAuthPolicy pairings will reach Ready;
    # ungoverned test fixtures (unconfigured, distinct, etc.) stay Pending by design.
    local governed_models=("facebook-opt-125m-simulated" "premium-simulated-simulated-premium")
    echo "Waiting for governed MaaSModelRefs to be Ready (timeout: ${MAASMODELREF_TIMEOUT}s)..."
     local deadline=$((SECONDS + MAASMODELREF_TIMEOUT))
     local all_ready=false
 
     while [[ $SECONDS -lt $deadline ]]; do
         all_ready=true
        for model in "${governed_models[@]}"; do
            phase=$(oc get maasmodelref "$model" -n "$MODEL_NAMESPACE" -o jsonpath='{.status.phase}' 2>/dev/null || echo "")
             if [[ "$phase" != "Ready" ]]; then
                 all_ready=false
                 break
             fi
        done
 
        if $all_ready; then
            echo "✅ Governed MaaSModelRefs ready"
             break
         fi
 
         sleep 5
     done
 
    if ! $all_ready; then
        echo "❌ ERROR: Governed MaaSModelRefs did not reach Ready state within ${MAASMODELREF_TIMEOUT}s"
         echo "Dumping MaaSModelRef status:"
         oc get maasmodelrefs -n "$MODEL_NAMESPACE" -o yaml || true
         echo "Dumping controller logs:"