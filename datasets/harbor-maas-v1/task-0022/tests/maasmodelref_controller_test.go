 	maasv1alpha1 "github.com/opendatahub-io/models-as-a-service/maas-controller/api/maas/v1alpha1"
 )
 
var (
	testGatewayName      = "maas-default-gateway"
	testGatewayNamespace = "openshift-ingress"
)

 // fakeHandler is a test-only BackendHandler that returns preconfigured values.
 type fakeHandler struct {
 	endpoint string
 
 // newLLMISvcRoute is a helper function to create a HTTPRoute resource.
 func newLLMISvcRoute(llmisvcName, ns string) *gatewayapiv1.HTTPRoute {
	gwNS := gatewayapiv1.Namespace(testGatewayNamespace)
 	return &gatewayapiv1.HTTPRoute{
 		ObjectMeta: metav1.ObjectMeta{
 			Name:      llmisvcName + "-route",
 			Hostnames: []gatewayapiv1.Hostname{"model.example.com"},
 			CommonRouteSpec: gatewayapiv1.CommonRouteSpec{
 				ParentRefs: []gatewayapiv1.ParentReference{{
					Name:      gatewayapiv1.ObjectName(testGatewayName),
 					Namespace: &gwNS,
 				}},
 			},
 		WithIndex(&maasv1alpha1.MaaSModelRef{}, modelRefNameIndex, modelRefNameIndexer).
 		WithIndex(&maasv1alpha1.MaaSSubscription{}, modelRefIndexKey, subscriptionModelRefIndexer).
 		Build()
	return &MaaSModelRefReconciler{
		Client:           c,
		Scheme:           scheme,
		GatewayName:      testGatewayName,
		GatewayNamespace: testGatewayNamespace,
	}, c
 }
 
 // assertReadyCondition checks that the conditions slice contains a Ready condition
 // --- Tests ---
 
 func TestMaaSModelRefReconciler_gatewayName(t *testing.T) {
	t.Run("empty_when_unset", func(t *testing.T) {
 		r := &MaaSModelRefReconciler{}
		if got := r.gatewayName(); got != "" {
			t.Errorf("gatewayName() = %q, want %q", got, "")
 		}
 	})
 	t.Run("custom_when_set", func(t *testing.T) {
 				WithIndex(&maasv1alpha1.MaaSSubscription{}, modelRefIndexKey, subscriptionModelRefIndexer).
 				Build()
 
			r := &MaaSModelRefReconciler{Client: c, Scheme: scheme, GatewayName: testGatewayName, GatewayNamespace: testGatewayNamespace}
 			req := ctrl.Request{NamespacedName: types.NamespacedName{Name: "test-model", Namespace: "default"}}
 
 			if _, err := r.Reconcile(context.Background(), req); err != nil {
 }
 
 func TestMaaSModelRefReconciler_gatewayNamespace(t *testing.T) {
	t.Run("empty_when_unset", func(t *testing.T) {
 		r := &MaaSModelRefReconciler{}
		if got := r.gatewayNamespace(); got != "" {
			t.Errorf("gatewayNamespace() = %q, want %q", got, "")
 		}
 	})
 	t.Run("custom_when_set", func(t *testing.T) {
 		WithIndex(&maasv1alpha1.MaaSSubscription{}, modelRefIndexKey, subscriptionModelRefIndexer).
 		Build()
 
	r := &MaaSModelRefReconciler{Client: c, Scheme: scheme, GatewayName: testGatewayName, GatewayNamespace: testGatewayNamespace}
 	ctx := context.Background()
 	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: "dup-model", Namespace: "default"}}
 
 						WithObjects(existing).
 						Build()
 
					r := &MaaSModelRefReconciler{Client: c, Scheme: scheme, GatewayName: testGatewayName, GatewayNamespace: testGatewayNamespace}
 					if err := r.deleteGeneratedPoliciesByLabel(context.Background(), logr.Discard(), namespace, modelName, res.kind, res.group, res.version); err != nil {
 						t.Fatalf("deleteGeneratedPoliciesByLabel: unexpected error: %v", err)
 					}
 		}).
 		Build()
 
	r := &MaaSModelRefReconciler{Client: c, Scheme: scheme, GatewayName: testGatewayName, GatewayNamespace: testGatewayNamespace}
 	requests := r.mapHTTPRouteToMaaSModelRefs(ctx, route)
 	if len(requests) != 0 {
 		t.Errorf("mapHTTPRouteToMaaSModelRefs() with List error returned %d requests, want 0", len(requests))