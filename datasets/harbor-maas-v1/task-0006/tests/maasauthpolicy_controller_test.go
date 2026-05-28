 
 import (
 	"context"
	"strings"
 	"testing"
 
 	apierrors "k8s.io/apimachinery/pkg/api/errors"
 		t.Errorf("expected reason %q, got %q", maasv1alpha1.ReasonAcceptedEnforced, apStatus.Reason)
 	}
 }

// TestMaaSAuthPolicyReconciler_NoSpec verifies that a legacy auth policy created
// without a spec field is marked Failed without adding a finalizer.
func TestMaaSAuthPolicyReconciler_NoSpec(t *testing.T) {
	const namespace = "default"

	policy := &maasv1alpha1.MaaSAuthPolicy{
		ObjectMeta: metav1.ObjectMeta{Name: "no-spec", Namespace: namespace},
	}

	c := fake.NewClientBuilder().
		WithScheme(scheme).
		WithRESTMapper(testRESTMapper()).
		WithObjects(policy).
		WithStatusSubresource(&maasv1alpha1.MaaSAuthPolicy{}).
		Build()

	r := &MaaSAuthPolicyReconciler{Client: c, Scheme: scheme, MaaSAPINamespace: "maas-system"}
	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: policy.Name, Namespace: namespace}}
	if _, err := r.Reconcile(context.Background(), req); err != nil {
		t.Fatalf("Reconcile: unexpected error: %v", err)
	}

	got := &maasv1alpha1.MaaSAuthPolicy{}
	if err := c.Get(context.Background(), req.NamespacedName, got); err != nil {
		t.Fatalf("Get policy: %v", err)
	}

	if len(got.Finalizers) > 0 {
		t.Errorf("expected no finalizers, got %v", got.Finalizers)
	}

	if got.Status.Phase != maasv1alpha1.PhaseInvalid {
		t.Errorf("phase = %q, want %q", got.Status.Phase, maasv1alpha1.PhaseInvalid)
	}

	ready := apimeta.FindStatusCondition(got.Status.Conditions, "Ready")
	if ready == nil {
		t.Fatal("Ready condition not found")
	}
	if ready.Status != metav1.ConditionFalse {
		t.Errorf("Ready.Status = %q, want %q", ready.Status, metav1.ConditionFalse)
	}
	if ready.Reason != string(maasv1alpha1.ReasonInvalidSpec) {
		t.Errorf("Ready.Reason = %q, want %q", ready.Reason, maasv1alpha1.ReasonInvalidSpec)
	}
	if !strings.Contains(ready.Message, "spec is required") {
		t.Errorf("Ready.Message = %q, expected it to contain %q", ready.Message, "spec is required")
	}
}