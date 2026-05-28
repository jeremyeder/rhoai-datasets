 	}
 
 	// Reconcile deletion of modelA
	r := &MaaSModelRefReconciler{Client: c, Scheme: scheme, GatewayName: "maas-default-gateway", GatewayNamespace: "openshift-ingress"}
 	reqA := ctrl.Request{NamespacedName: types.NamespacedName{Name: modelName, Namespace: namespaceA}}
 	if _, err := r.Reconcile(context.Background(), reqA); err != nil {
 		t.Fatalf("Reconcile modelA deletion: unexpected error: %v", err)