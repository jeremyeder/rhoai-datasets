   ok "Istio networking configured"
 fi
 
# ─── Step 9: MaaS controller reconciles platform ───────────────────────────
 
step "Deploying MaaS controller"
 
 # Handle arm64: check if images need local build
 if [[ "$ARCH" == "arm64" ]]; then
 # Create subscription namespace
 kubectl create namespace "$SUBSCRIPTION_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
 
# Build a small local kustomize wrapper for maas-controller only.
# The controller then reconciles maas-api and payload-processing via Tenant.
 TEMP_DIR=$(mktemp -d)
 trap 'rm -rf "$TEMP_DIR"' EXIT
 
# Symlink deployment dir so kustomize can reference it with relative paths.
 ln -s "$PROJECT_ROOT/deployment" "$TEMP_DIR/deployment"
 
 # Create Kind-specific params.env
 cat > "$TEMP_DIR/params.env" <<EOF
 maas-api-image=${MAAS_API_IMAGE}
 maas-controller-image=${MAAS_CONTROLLER_IMAGE}
payload-processing-image=${BBR_IMAGE}
 maas-api-key-cleanup-image=docker.io/curlimages/curl:latest
 EOF
 
# Create a live maas-parameters ConfigMap with image values consumed by
# RELATED_IMAGE_* env vars on the controller Deployment.
 cat > "$TEMP_DIR/kustomization.yaml" <<EOF
 apiVersion: kustomize.config.k8s.io/v1beta1
 kind: Kustomization
   disableNameSuffixHash: true
 
 resources:
   - deployment/base/maas-controller/default
 
 patches:
   - target:
       kind: Deployment
      name: maas-controller
    patch: |
      apiVersion: apps/v1
       kind: Deployment
      metadata:
        name: maas-controller
      spec:
        template:
          spec:
            containers:
            - name: manager
              image: ${MAAS_CONTROLLER_IMAGE}
              env:
              - name: GATEWAY_NAMESPACE
                value: ${GATEWAY_NAMESPACE}
 EOF
 
 echo "  Building kustomize manifests..."
 " > "$TEMP_DIR/filtered.yaml"
 
 if ! kubectl apply --server-side=true --force-conflicts -f "$TEMP_DIR/filtered.yaml" 2>&1 | tail -15; then
  fail "Failed to apply MaaS controller manifests"
   exit 1
 fi
 
 echo "  Waiting for MaaS controller..."
 kubectl rollout status deployment/maas-controller -n "$MAAS_NAMESPACE" --timeout=180s 2>/dev/null || \
   warn "maas-controller not ready yet"
 
echo "  Waiting for controller to reconcile maas-api..."
for _i in $(seq 1 36); do
  kubectl get deployment maas-api -n "$MAAS_NAMESPACE" &>/dev/null && break
  sleep 5
done
if kubectl get deployment maas-api -n "$MAAS_NAMESPACE" &>/dev/null; then
  kubectl rollout status deployment/maas-api -n "$MAAS_NAMESPACE" --timeout=180s 2>/dev/null || \
    warn "maas-api not ready yet"
else
  warn "maas-api deployment was not created by maas-controller"
fi

echo "  Waiting for controller to reconcile payload-processing..."
for _i in $(seq 1 36); do
  kubectl get deployment payload-processing -n "$GATEWAY_NAMESPACE" &>/dev/null && break
  sleep 5
done
if kubectl get deployment payload-processing -n "$GATEWAY_NAMESPACE" &>/dev/null; then
  # Disable sidecar injection on payload-processing (BBR uses self-signed TLS for ext-proc).
  kubectl patch deployment payload-processing -n "$GATEWAY_NAMESPACE" --type=merge \
    -p='{"spec":{"template":{"metadata":{"annotations":{"sidecar.istio.io/inject":"false"}}}}}' 2>/dev/null || true
  kubectl rollout status deployment/payload-processing -n "$GATEWAY_NAMESPACE" --timeout=180s 2>/dev/null || \
    warn "payload-processing not ready yet"
else
  warn "payload-processing deployment was not created by maas-controller"
fi

ok "MaaS controller deployed and reconciled platform resources"
 
 # ─── Step 10b: Test fixtures ────────────────────────────────────────────────
 