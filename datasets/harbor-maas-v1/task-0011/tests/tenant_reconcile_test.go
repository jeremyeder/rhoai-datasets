 	. "github.com/onsi/gomega"
 )
 
var (
	testTenantGatewayName      = "maas-default-gateway"
	testTenantGatewayNamespace = "openshift-ingress"
)

 func tenantTestScheme(t *testing.T) *runtime.Scheme {
 	t.Helper()
 	s := runtime.NewScheme()
 		Build()
 
 	r := &TenantReconciler{
		Client:           cl,
		Scheme:           s,
		AppNamespace:     testNS,
		GatewayName:      testTenantGatewayName,
		GatewayNamespace: testTenantGatewayNamespace,
 	}
 
 	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: tenant.Name, Namespace: testNS}}
 		Build()
 
 	r := &TenantReconciler{
		Client:           cl,
		Scheme:           s,
		AppNamespace:     testNS,
		GatewayName:      testTenantGatewayName,
		GatewayNamespace: testTenantGatewayNamespace,
 	}
 
 	res, err := r.Reconcile(context.Background(), ctrl.Request{
 		Build()
 
 	r := &TenantReconciler{
		Client:           cl,
		Scheme:           s,
		AppNamespace:     testNS,
		GatewayName:      testTenantGatewayName,
		GatewayNamespace: testTenantGatewayNamespace,
 	}
 
 	res, err := r.Reconcile(context.Background(), ctrl.Request{
 		Build()
 
 	r := &TenantReconciler{
		Client:           cl,
		Scheme:           s,
		AppNamespace:     testNS,
		GatewayName:      testTenantGatewayName,
		GatewayNamespace: testTenantGatewayNamespace,
 	}
 
 	res, err := r.Reconcile(context.Background(), ctrl.Request{
 		Build()
 
 	r := &TenantReconciler{
		Client:           cl,
		Scheme:           s,
		AppNamespace:     testNS,
		GatewayName:      testTenantGatewayName,
		GatewayNamespace: testTenantGatewayNamespace,
 	}
 
 	res, err := r.Reconcile(context.Background(), ctrl.Request{
 		Build()
 
 	r := &TenantReconciler{
		Client:           cl,
		Scheme:           s,
		AppNamespace:     testNS,
		GatewayName:      testTenantGatewayName,
		GatewayNamespace: testTenantGatewayNamespace,
 	}
 
 	res, err := r.Reconcile(context.Background(), ctrl.Request{
 		Build()
 
 	r := &TenantReconciler{
		Client:           cl,
		Scheme:           s,
		AppNamespace:     testNS,
		GatewayName:      testTenantGatewayName,
		GatewayNamespace: testTenantGatewayNamespace,
 	}
 
 	res, err := r.Reconcile(context.Background(), ctrl.Request{
 		Build()
 
 	r := &TenantReconciler{
		Client:           cl,
		Scheme:           s,
		AppNamespace:     testNS,
		GatewayName:      testTenantGatewayName,
		GatewayNamespace: testTenantGatewayNamespace,
 	}
 
 	res, err := r.Reconcile(context.Background(), ctrl.Request{
 		Build()
 
 	r := &TenantReconciler{
		Client:           cl,
		Scheme:           s,
		AppNamespace:     testNS,
		GatewayName:      testTenantGatewayName,
		GatewayNamespace: testTenantGatewayNamespace,
 	}
 
 	res, err := r.Reconcile(context.Background(), ctrl.Request{
 		Build()
 
 	r := &TenantReconciler{
		Client:           cl,
		Scheme:           s,
		AppNamespace:     testNS,
		GatewayName:      testTenantGatewayName,
		GatewayNamespace: testTenantGatewayNamespace,
 	}
 
 	res, err := r.Reconcile(context.Background(), ctrl.Request{
 		Build()
 
 	r := &TenantReconciler{
		Client:           cl,
		Scheme:           s,
		AppNamespace:     "models-as-a-service",
		GatewayName:      testTenantGatewayName,
		GatewayNamespace: testTenantGatewayNamespace,
 	}
 
 	res, err := r.Reconcile(context.Background(), ctrl.Request{