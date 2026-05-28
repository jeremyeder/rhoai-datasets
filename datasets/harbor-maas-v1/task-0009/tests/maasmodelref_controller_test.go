 		WithObjects(objects...).
 		WithStatusSubresource(&maasv1alpha1.MaaSModelRef{}).
 		WithIndex(&maasv1alpha1.MaaSModelRef{}, modelRefNameIndex, modelRefNameIndexer).
		WithIndex(&maasv1alpha1.MaaSSubscription{}, modelRefIndexKey, subscriptionModelRefIndexer).
 		Build()
 	return &MaaSModelRefReconciler{Client: c, Scheme: scheme}, c
 }
 
 // assertReadyCondition checks that the conditions slice contains a Ready condition
 // with the expected status and reason.
 func assertReadyCondition(t *testing.T, conditions []metav1.Condition, wantStatus metav1.ConditionStatus, wantReason string) {
	t.Helper()
	assertCondition(t, conditions, "Ready", wantStatus, wantReason)
}

// assertCondition checks that the conditions slice contains a condition of the given
// type with the expected status and reason.
func assertCondition(t *testing.T, conditions []metav1.Condition, condType string, wantStatus metav1.ConditionStatus, wantReason string) {
 	t.Helper()
 	for _, c := range conditions {
		if c.Type == condType {
 			if c.Status != wantStatus {
				t.Errorf("%s condition Status = %q, want %q", condType, c.Status, wantStatus)
 			}
 			if c.Reason != wantReason {
				t.Errorf("%s condition Reason = %q, want %q", condType, c.Reason, wantReason)
 			}
 			return
 		}
 	}
	t.Errorf("%s condition not found in status conditions", condType)
 }
 
 // --- Tests ---
 					EndpointOverride: tt.endpointOverride,
 				},
 			}
			sub := newMaaSSubscription("sub1", "admin-ns", "team-a", "test-model", 100)
			sub.Spec.ModelRefs[0].Namespace = "default"
			auth := newMaaSAuthPolicy("auth1", "admin-ns", "team-a",
				maasv1alpha1.ModelRef{Name: "test-model", Namespace: "default"})
 
 			c := fake.NewClientBuilder().
 				WithScheme(scheme).
				WithObjects(model, sub, auth).
 				WithStatusSubresource(model).
				WithIndex(&maasv1alpha1.MaaSSubscription{}, modelRefIndexKey, subscriptionModelRefIndexer).
 				Build()
 
 			r := &MaaSModelRefReconciler{Client: c, Scheme: scheme}
 	route := newLLMISvcRoute(llmisvcName, ns)
 	llmisvc := newLLMISvc(llmisvcName, ns, corev1.ConditionFalse)
 	model := newMaaSModelRef(modelName, ns, "LLMInferenceService", llmisvcName)
	sub := newMaaSSubscription("sub1", "admin-ns", "team-a", modelName, 100)
	sub.Spec.ModelRefs[0].Namespace = ns
	auth := newMaaSAuthPolicy("auth1", "admin-ns", "team-a",
		maasv1alpha1.ModelRef{Name: modelName, Namespace: ns})
	r, c := newTestReconciler(model, route, llmisvc, sub, auth)
 	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: modelName, Namespace: ns}}
 
	// --- Phase 1: reconcile while llmisvc is not-ready -> model enters Unhealthy (governed but runtime not ready) ---
 
 	if _, err := r.Reconcile(ctx, req); err != nil {
 		t.Fatalf("Reconcile (llmisvc not-ready): %v", err)
 	if err := c.Get(ctx, req.NamespacedName, got); err != nil {
 		t.Fatalf("Get after first reconcile: %v", err)
 	}
	if got.Status.Phase != "Unhealthy" {
		t.Fatalf("after first reconcile: Phase = %q, want Unhealthy (governed but runtime not ready)", got.Status.Phase)
 	}
 	assertReadyCondition(t, got.Status.Conditions, metav1.ConditionFalse, "BackendNotReady")
 
 // TestMaaSModelReconciler_LLMISvcReadyToNotReady_ModelBecomesPending verifies that when
 // a backing LLMInferenceService transitions from ready to not-ready, the MaaSModelRef
 // is automatically re-reconciled and moves from Ready back to Pending.
func TestMaaSModelReconciler_LLMISvcReadyToNotReady_ModelBecomesUnhealthy(t *testing.T) {
 	ctx := context.Background()
 	const (
 		modelName   = "test-model"
 	route := newLLMISvcRoute(llmisvcName, ns)
 	llmisvc := newLLMISvc(llmisvcName, ns, corev1.ConditionTrue)
 	model := newMaaSModelRef(modelName, ns, "LLMInferenceService", llmisvcName)
	sub := newMaaSSubscription("sub1", "admin-ns", "team-a", modelName, 100)
	sub.Spec.ModelRefs[0].Namespace = ns
	auth := newMaaSAuthPolicy("auth1", "admin-ns", "team-a",
		maasv1alpha1.ModelRef{Name: modelName, Namespace: ns})
	r, c := newTestReconciler(model, route, llmisvc, sub, auth)
 	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: modelName, Namespace: ns}}
 
 	// --- Phase 1: reconcile while llmisvc is ready -> model enters Ready ---
 	}
 	assertReadyCondition(t, got.Status.Conditions, metav1.ConditionTrue, "Reconciled")
 
	// --- Phase 2: KServe marks the llmisvc not-ready -> model should become Unhealthy (governed but runtime failed) ---
 
 	currentLLMISvc := &kservev1alpha1.LLMInferenceService{}
 	if err := c.Get(ctx, types.NamespacedName{Name: llmisvcName, Namespace: ns}, currentLLMISvc); err != nil {
 	if err := c.Get(ctx, req.NamespacedName, final); err != nil {
 		t.Fatalf("Get MaaSModelRef after llmisvc became not-ready: %v", err)
 	}
	if final.Status.Phase != "Unhealthy" {
		t.Errorf("after llmisvc became not-ready: Phase = %q, want Unhealthy (governed but runtime failed)", final.Status.Phase)
 	}
	assertCondition(t, final.Status.Conditions, "GovernanceAttached", metav1.ConditionTrue, "GovernancePaired")
	assertCondition(t, final.Status.Conditions, "RuntimeReady", metav1.ConditionFalse, "RuntimeHealthFailure")
 	assertReadyCondition(t, final.Status.Conditions, metav1.ConditionFalse, "BackendNotReady")
 }
 
 	// Start with MaaSModelRef and ready LLMInferenceService, but NO HTTPRoute
 	llmisvc := newLLMISvc(llmisvcName, ns, corev1.ConditionTrue)
 	model := newMaaSModelRef(modelName, ns, "LLMInferenceService", llmisvcName)
	sub := newMaaSSubscription("sub1", "admin-ns", "team-a", modelName, 100)
	sub.Spec.ModelRefs[0].Namespace = ns
	auth := newMaaSAuthPolicy("auth1", "admin-ns", "team-a",
		maasv1alpha1.ModelRef{Name: modelName, Namespace: ns})
	r, c := newTestReconciler(model, llmisvc, sub, auth)
 	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: modelName, Namespace: ns}}
 
 	// --- Phase 1: Reconcile without HTTPRoute -> should enter Pending ---
 			ModelRef: maasv1alpha1.ModelReference{Kind: testKind, Name: "backend"},
 		},
 	}
	sub := newMaaSSubscription("sub1", "admin-ns", "team-a", "dup-model", 100)
	sub.Spec.ModelRefs[0].Namespace = "default"
	auth := newMaaSAuthPolicy("auth1", "admin-ns", "team-a",
		maasv1alpha1.ModelRef{Name: "dup-model", Namespace: "default"})
 
 	c := fake.NewClientBuilder().
 		WithScheme(scheme).
		WithObjects(model, sub, auth).
 		WithStatusSubresource(model).
		WithIndex(&maasv1alpha1.MaaSSubscription{}, modelRefIndexKey, subscriptionModelRefIndexer).
 		Build()
 
 	r := &MaaSModelRefReconciler{Client: c, Scheme: scheme}
 
 	assertReadyCondition(t, got.Status.Conditions, metav1.ConditionFalse, "InvalidSpec")
 }

// --- Governance Tests ---

// TestGovernance_NoPairing verifies that a MaaSModelRef with no MaaSSubscription
// or MaaSAuthPolicy is set to Pending with GovernanceAttached: False.
func TestGovernance_NoPairing(t *testing.T) {
	const testKind = "_test_gov_no_pair"
	backendHandlerFactories[testKind] = func(_ *MaaSModelRefReconciler) BackendHandler {
		return &fakeHandler{endpoint: "https://model.example.com", ready: true}
	}
	defer delete(backendHandlerFactories, testKind)

	model := newMaaSModelRef("gov-model", "default", testKind, "backend")
	r, c := newTestReconciler(model)
	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: "gov-model", Namespace: "default"}}

	if _, err := r.Reconcile(context.Background(), req); err != nil {
		t.Fatalf("Reconcile: %v", err)
	}

	got := &maasv1alpha1.MaaSModelRef{}
	if err := c.Get(context.Background(), req.NamespacedName, got); err != nil {
		t.Fatalf("Get: %v", err)
	}

	if got.Status.Phase != "Pending" {
		t.Errorf("Phase = %q, want Pending", got.Status.Phase)
	}
	assertCondition(t, got.Status.Conditions, "GovernanceAttached", metav1.ConditionFalse, "NoPairingFound")
	assertCondition(t, got.Status.Conditions, "RuntimeReady", metav1.ConditionTrue, "RuntimeHealthy")
	assertReadyCondition(t, got.Status.Conditions, metav1.ConditionFalse, "BackendNotReady")
}

// TestGovernance_ActivePairing verifies that a MaaSModelRef with both an active
// MaaSSubscription and MaaSAuthPolicy becomes Ready with GovernanceAttached: True.
func TestGovernance_ActivePairing(t *testing.T) {
	const testKind = "_test_gov_active"
	backendHandlerFactories[testKind] = func(_ *MaaSModelRefReconciler) BackendHandler {
		return &fakeHandler{endpoint: "https://model.example.com", ready: true}
	}
	defer delete(backendHandlerFactories, testKind)

	model := newMaaSModelRef("gov-model", "default", testKind, "backend")
	sub := newMaaSSubscription("sub1", "admin-ns", "team-a", "gov-model", 100)
	sub.Spec.ModelRefs[0].Namespace = "default"
	authPolicy := newMaaSAuthPolicy("auth1", "admin-ns", "team-a",
		maasv1alpha1.ModelRef{Name: "gov-model", Namespace: "default"})

	r, c := newTestReconciler(model, sub, authPolicy)
	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: "gov-model", Namespace: "default"}}

	if _, err := r.Reconcile(context.Background(), req); err != nil {
		t.Fatalf("Reconcile: %v", err)
	}

	got := &maasv1alpha1.MaaSModelRef{}
	if err := c.Get(context.Background(), req.NamespacedName, got); err != nil {
		t.Fatalf("Get: %v", err)
	}

	if got.Status.Phase != "Ready" {
		t.Errorf("Phase = %q, want Ready", got.Status.Phase)
	}
	assertCondition(t, got.Status.Conditions, "GovernanceAttached", metav1.ConditionTrue, "GovernancePaired")
	assertCondition(t, got.Status.Conditions, "RuntimeReady", metav1.ConditionTrue, "RuntimeHealthy")
	assertReadyCondition(t, got.Status.Conditions, metav1.ConditionTrue, "Reconciled")
}

// TestGovernance_PairingRemoved verifies that when a previously governed model
// loses its governance pairing, it transitions away from Ready with reason GovernanceGap.
func TestGovernance_PairingRemoved(t *testing.T) {
	const testKind = "_test_gov_removed"
	backendHandlerFactories[testKind] = func(_ *MaaSModelRefReconciler) BackendHandler {
		return &fakeHandler{endpoint: "https://model.example.com", ready: true}
	}
	defer delete(backendHandlerFactories, testKind)

	ctx := context.Background()
	model := newMaaSModelRef("gov-model", "default", testKind, "backend")
	sub := newMaaSSubscription("sub1", "admin-ns", "team-a", "gov-model", 100)
	sub.Spec.ModelRefs[0].Namespace = "default"
	authPolicy := newMaaSAuthPolicy("auth1", "admin-ns", "team-a",
		maasv1alpha1.ModelRef{Name: "gov-model", Namespace: "default"})

	r, c := newTestReconciler(model, sub, authPolicy)
	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: "gov-model", Namespace: "default"}}

	// Phase 1: reconcile with governance -> Ready
	if _, err := r.Reconcile(ctx, req); err != nil {
		t.Fatalf("Reconcile #1: %v", err)
	}
	got := &maasv1alpha1.MaaSModelRef{}
	if err := c.Get(ctx, req.NamespacedName, got); err != nil {
		t.Fatalf("Get after #1: %v", err)
	}
	if got.Status.Phase != "Ready" {
		t.Fatalf("Phase after #1 = %q, want Ready", got.Status.Phase)
	}

	// Phase 2: delete the subscription -> governance lost
	if err := c.Delete(ctx, sub); err != nil {
		t.Fatalf("Delete sub: %v", err)
	}
	if _, err := r.Reconcile(ctx, req); err != nil {
		t.Fatalf("Reconcile #2: %v", err)
	}
	if err := c.Get(ctx, req.NamespacedName, got); err != nil {
		t.Fatalf("Get after #2: %v", err)
	}

	if got.Status.Phase != "Pending" {
		t.Errorf("Phase after governance loss = %q, want Pending", got.Status.Phase)
	}
	assertCondition(t, got.Status.Conditions, "GovernanceAttached", metav1.ConditionFalse, "GovernanceGap")
}

// TestGovernance_RuntimeFailureWithGovernance verifies that when a governed model
// has a runtime/health failure, GovernanceAttached stays True and RuntimeReady is False.
func TestGovernance_RuntimeFailureWithGovernance(t *testing.T) {
	const testKind = "_test_gov_runtime_fail"
	backendHandlerFactories[testKind] = func(_ *MaaSModelRefReconciler) BackendHandler {
		return &fakeHandler{endpoint: "", ready: false}
	}
	defer delete(backendHandlerFactories, testKind)

	model := newMaaSModelRef("gov-model", "default", testKind, "backend")
	sub := newMaaSSubscription("sub1", "admin-ns", "team-a", "gov-model", 100)
	sub.Spec.ModelRefs[0].Namespace = "default"
	authPolicy := newMaaSAuthPolicy("auth1", "admin-ns", "team-a",
		maasv1alpha1.ModelRef{Name: "gov-model", Namespace: "default"})

	r, c := newTestReconciler(model, sub, authPolicy)
	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: "gov-model", Namespace: "default"}}

	if _, err := r.Reconcile(context.Background(), req); err != nil {
		t.Fatalf("Reconcile: %v", err)
	}

	got := &maasv1alpha1.MaaSModelRef{}
	if err := c.Get(context.Background(), req.NamespacedName, got); err != nil {
		t.Fatalf("Get: %v", err)
	}

	if got.Status.Phase != "Unhealthy" {
		t.Errorf("Phase = %q, want Unhealthy", got.Status.Phase)
	}
	assertCondition(t, got.Status.Conditions, "GovernanceAttached", metav1.ConditionTrue, "GovernancePaired")
	assertCondition(t, got.Status.Conditions, "RuntimeReady", metav1.ConditionFalse, "RuntimeHealthFailure")
	assertReadyCondition(t, got.Status.Conditions, metav1.ConditionFalse, "BackendNotReady")
}

// TestGovernance_BothFailures verifies that when both governance and runtime fail,
// the status reflects both issues simultaneously.
func TestGovernance_BothFailures(t *testing.T) {
	const testKind = "_test_gov_both_fail"
	backendHandlerFactories[testKind] = func(_ *MaaSModelRefReconciler) BackendHandler {
		return &fakeHandler{endpoint: "", ready: false}
	}
	defer delete(backendHandlerFactories, testKind)

	model := newMaaSModelRef("gov-model", "default", testKind, "backend")
	r, c := newTestReconciler(model)
	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: "gov-model", Namespace: "default"}}

	if _, err := r.Reconcile(context.Background(), req); err != nil {
		t.Fatalf("Reconcile: %v", err)
	}

	got := &maasv1alpha1.MaaSModelRef{}
	if err := c.Get(context.Background(), req.NamespacedName, got); err != nil {
		t.Fatalf("Get: %v", err)
	}

	if got.Status.Phase != "Pending" {
		t.Errorf("Phase = %q, want Pending", got.Status.Phase)
	}
	assertCondition(t, got.Status.Conditions, "GovernanceAttached", metav1.ConditionFalse, "NoPairingFound")
	assertCondition(t, got.Status.Conditions, "RuntimeReady", metav1.ConditionFalse, "RuntimeHealthFailure")
}

// TestGovernance_NoAdminCRNamesInStatus verifies that no subscription or auth policy
// names, namespaces, or UIDs appear in MaaSModelRef.status.
func TestGovernance_NoAdminCRNamesInStatus(t *testing.T) {
	const testKind = "_test_gov_privacy"
	backendHandlerFactories[testKind] = func(_ *MaaSModelRefReconciler) BackendHandler {
		return &fakeHandler{endpoint: "https://model.example.com", ready: true}
	}
	defer delete(backendHandlerFactories, testKind)

	model := newMaaSModelRef("gov-model", "default", testKind, "backend")
	sub := &maasv1alpha1.MaaSSubscription{
		ObjectMeta: metav1.ObjectMeta{Name: "secret-admin-subscription", Namespace: "admin-confidential-ns"},
		Spec: maasv1alpha1.MaaSSubscriptionSpec{
			Owner:     maasv1alpha1.OwnerSpec{Groups: []maasv1alpha1.GroupReference{{Name: "team-a"}}},
			ModelRefs: []maasv1alpha1.ModelSubscriptionRef{{Name: "gov-model", Namespace: "default", TokenRateLimits: []maasv1alpha1.TokenRateLimit{{Limit: 100, Window: "1m"}}}},
		},
	}
	authPolicy := &maasv1alpha1.MaaSAuthPolicy{
		ObjectMeta: metav1.ObjectMeta{Name: "secret-admin-policy", Namespace: "admin-confidential-ns"},
		Spec: maasv1alpha1.MaaSAuthPolicySpec{
			ModelRefs: []maasv1alpha1.ModelRef{{Name: "gov-model", Namespace: "default"}},
			Subjects:  maasv1alpha1.SubjectSpec{Groups: []maasv1alpha1.GroupReference{{Name: "team-a"}}},
		},
	}

	r, c := newTestReconciler(model, sub, authPolicy)
	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: "gov-model", Namespace: "default"}}

	if _, err := r.Reconcile(context.Background(), req); err != nil {
		t.Fatalf("Reconcile: %v", err)
	}

	got := &maasv1alpha1.MaaSModelRef{}
	if err := c.Get(context.Background(), req.NamespacedName, got); err != nil {
		t.Fatalf("Get: %v", err)
	}

	// Check that no admin CR names/namespaces leak into conditions
	sensitiveStrings := []string{
		"secret-admin-subscription",
		"secret-admin-policy",
		"admin-confidential-ns",
	}
	for _, cond := range got.Status.Conditions {
		for _, s := range sensitiveStrings {
			if containsString(cond.Message, s) {
				t.Errorf("condition %q message contains admin CR reference %q: %q", cond.Type, s, cond.Message)
			}
			if containsString(cond.Reason, s) {
				t.Errorf("condition %q reason contains admin CR reference %q: %q", cond.Type, s, cond.Reason)
			}
		}
	}
}

// TestGovernance_SubscriptionOnly_NotGoverned verifies that having only a
// MaaSSubscription (no MaaSAuthPolicy) does not make the model governed.
func TestGovernance_SubscriptionOnly_NotGoverned(t *testing.T) {
	const testKind = "_test_gov_sub_only"
	backendHandlerFactories[testKind] = func(_ *MaaSModelRefReconciler) BackendHandler {
		return &fakeHandler{endpoint: "https://model.example.com", ready: true}
	}
	defer delete(backendHandlerFactories, testKind)

	model := newMaaSModelRef("gov-model", "default", testKind, "backend")
	sub := newMaaSSubscription("sub1", "admin-ns", "team-a", "gov-model", 100)
	sub.Spec.ModelRefs[0].Namespace = "default"

	r, c := newTestReconciler(model, sub)
	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: "gov-model", Namespace: "default"}}

	if _, err := r.Reconcile(context.Background(), req); err != nil {
		t.Fatalf("Reconcile: %v", err)
	}

	got := &maasv1alpha1.MaaSModelRef{}
	if err := c.Get(context.Background(), req.NamespacedName, got); err != nil {
		t.Fatalf("Get: %v", err)
	}

	if got.Status.Phase != "Pending" {
		t.Errorf("Phase = %q, want Pending (sub only, no auth policy)", got.Status.Phase)
	}
	assertCondition(t, got.Status.Conditions, "GovernanceAttached", metav1.ConditionFalse, "NoPairingFound")
}

// TestGovernance_AuthPolicyOnly_NotGoverned verifies that having only a
// MaaSAuthPolicy (no MaaSSubscription) does not make the model governed.
func TestGovernance_AuthPolicyOnly_NotGoverned(t *testing.T) {
	const testKind = "_test_gov_auth_only"
	backendHandlerFactories[testKind] = func(_ *MaaSModelRefReconciler) BackendHandler {
		return &fakeHandler{endpoint: "https://model.example.com", ready: true}
	}
	defer delete(backendHandlerFactories, testKind)

	model := newMaaSModelRef("gov-model", "default", testKind, "backend")
	authPolicy := newMaaSAuthPolicy("auth1", "admin-ns", "team-a",
		maasv1alpha1.ModelRef{Name: "gov-model", Namespace: "default"})

	r, c := newTestReconciler(model, authPolicy)
	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: "gov-model", Namespace: "default"}}

	if _, err := r.Reconcile(context.Background(), req); err != nil {
		t.Fatalf("Reconcile: %v", err)
	}

	got := &maasv1alpha1.MaaSModelRef{}
	if err := c.Get(context.Background(), req.NamespacedName, got); err != nil {
		t.Fatalf("Get: %v", err)
	}

	if got.Status.Phase != "Pending" {
		t.Errorf("Phase = %q, want Pending (auth policy only, no sub)", got.Status.Phase)
	}
	assertCondition(t, got.Status.Conditions, "GovernanceAttached", metav1.ConditionFalse, "NoPairingFound")
}

// TestGovernance_MapSubscriptionToModels verifies that the mapper function
// correctly maps MaaSSubscription changes to the referenced MaaSModelRefs.
func TestGovernance_MapSubscriptionToModels(t *testing.T) {
	sub := &maasv1alpha1.MaaSSubscription{
		ObjectMeta: metav1.ObjectMeta{Name: "sub1", Namespace: "admin-ns"},
		Spec: maasv1alpha1.MaaSSubscriptionSpec{
			Owner: maasv1alpha1.OwnerSpec{Groups: []maasv1alpha1.GroupReference{{Name: "team-a"}}},
			ModelRefs: []maasv1alpha1.ModelSubscriptionRef{
				{Name: "model-a", Namespace: "ns-a", TokenRateLimits: []maasv1alpha1.TokenRateLimit{{Limit: 100, Window: "1m"}}},
				{Name: "model-b", Namespace: "ns-b", TokenRateLimits: []maasv1alpha1.TokenRateLimit{{Limit: 100, Window: "1m"}}},
			},
		},
	}

	r := &MaaSModelRefReconciler{}
	requests := r.mapMaaSSubscriptionToMaaSModelRefs(context.Background(), sub)

	if len(requests) != 2 {
		t.Fatalf("expected 2 requests, got %d: %v", len(requests), requests)
	}

	names := map[string]bool{}
	for _, req := range requests {
		names[req.Namespace+"/"+req.Name] = true
	}
	if !names["ns-a/model-a"] {
		t.Errorf("expected ns-a/model-a in requests")
	}
	if !names["ns-b/model-b"] {
		t.Errorf("expected ns-b/model-b in requests")
	}
}

// TestGovernance_MapAuthPolicyToModels verifies that the mapper function
// correctly maps MaaSAuthPolicy changes to the referenced MaaSModelRefs.
func TestGovernance_MapAuthPolicyToModels(t *testing.T) {
	policy := &maasv1alpha1.MaaSAuthPolicy{
		ObjectMeta: metav1.ObjectMeta{Name: "auth1", Namespace: "admin-ns"},
		Spec: maasv1alpha1.MaaSAuthPolicySpec{
			ModelRefs: []maasv1alpha1.ModelRef{
				{Name: "model-a", Namespace: "ns-a"},
				{Name: "model-b", Namespace: "ns-b"},
			},
			Subjects: maasv1alpha1.SubjectSpec{Groups: []maasv1alpha1.GroupReference{{Name: "team-a"}}},
		},
	}

	r := &MaaSModelRefReconciler{}
	requests := r.mapMaaSAuthPolicyToMaaSModelRefs(context.Background(), policy)

	if len(requests) != 2 {
		t.Fatalf("expected 2 requests, got %d: %v", len(requests), requests)
	}

	names := map[string]bool{}
	for _, req := range requests {
		names[req.Namespace+"/"+req.Name] = true
	}
	if !names["ns-a/model-a"] {
		t.Errorf("expected ns-a/model-a in requests")
	}
	if !names["ns-b/model-b"] {
		t.Errorf("expected ns-b/model-b in requests")
	}
}