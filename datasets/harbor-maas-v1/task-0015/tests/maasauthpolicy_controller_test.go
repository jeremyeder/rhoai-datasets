 		t.Errorf("Ready.Message = %q, expected it to contain %q", ready.Message, "spec is required")
 	}
 }

// TestMaaSAuthPolicyReconciler_StaleEvent_NoOp verifies the W4a contract: a reconcile
// request for a MaaSAuthPolicy that no longer exists (stale queue entry or deleted-race)
// returns cleanly without error. After the W4a fix, fetchOIDCConfig is only called after
// confirming the policy CR exists, so the Tenant is not queried on stale events.
func TestMaaSAuthPolicyReconciler_StaleEvent_NoOp(t *testing.T) {
	// Empty store — policy was deleted before this reconcile fired.
	c := fake.NewClientBuilder().
		WithScheme(scheme).
		WithRESTMapper(testRESTMapper()).
		Build()

	r := &MaaSAuthPolicyReconciler{Client: c, Scheme: scheme, MaaSAPINamespace: "maas-system"}
	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: "gone-policy", Namespace: "default"}}

	res, err := r.Reconcile(context.Background(), req)
	if err != nil {
		t.Fatalf("expected no error for stale event, got: %v", err)
	}
	if res != (ctrl.Result{}) {
		t.Errorf("expected empty Result, got %+v", res)
	}
}