 		t.Errorf("mapHTTPRouteToMaaSModelRefs() with List error returned %d requests, want 0", len(requests))
 	}
 }

// TestMaaSModelRefReconciler_NoSpec verifies that a legacy model ref created
// without a spec field is marked Failed without adding a finalizer.
func TestMaaSModelRefReconciler_NoSpec(t *testing.T) {
	model := &maasv1alpha1.MaaSModelRef{
		ObjectMeta: metav1.ObjectMeta{Name: "no-spec", Namespace: "default"},
	}

	r, c := newTestReconciler(model)
	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: model.Name, Namespace: model.Namespace}}
	if _, err := r.Reconcile(context.Background(), req); err != nil {
		t.Fatalf("Reconcile: unexpected error: %v", err)
	}

	got := &maasv1alpha1.MaaSModelRef{}
	if err := c.Get(context.Background(), req.NamespacedName, got); err != nil {
		t.Fatalf("Get model: %v", err)
	}

	if len(got.Finalizers) > 0 {
		t.Errorf("expected no finalizers, got %v", got.Finalizers)
	}

	if got.Status.Phase != "Invalid" {
		t.Errorf("phase = %q, want %q", got.Status.Phase, "Invalid")
	}

	assertReadyCondition(t, got.Status.Conditions, metav1.ConditionFalse, "InvalidSpec")
}