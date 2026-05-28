 		g.Expect(res).To(Equal(ctrl.Result{}))
 	})
 
	t.Run("no-op when Deployment is terminating but CleanupFinalizer is absent", func(t *testing.T) {
		// W4b contract: if the finalizer was never set (e.g. controller first deployed against
		// a Deployment that is immediately deleted), Reconcile returns cleanly with no error
		// and skips all teardown rather than panicking or re-queuing indefinitely.
		//
		// The fake client refuses to store objects with DeletionTimestamp but no finalizers, so we
		// use a placeholder finalizer (not CleanupFinalizer) and Delete to trigger DeletionTimestamp.
		g := NewWithT(t)
		const placeholderFinalizer = "test/placeholder"
		dep := &appsv1.Deployment{ObjectMeta: metav1.ObjectMeta{
			Name:       depName,
			Namespace:  depNS,
			Finalizers: []string{placeholderFinalizer},
		}}
		cli := fake.NewClientBuilder().WithScheme(selfDepScheme(t)).WithObjects(dep).Build()

		g.Expect(cli.Delete(t.Context(), dep)).To(Succeed())

		r := &LifecycleReconciler{Client: cli, DeploymentName: depName, DeploymentNS: depNS, TenantNamespace: tenantNS}
		res, err := r.Reconcile(t.Context(), req)
		g.Expect(err).ShouldNot(HaveOccurred())
		g.Expect(res).To(Equal(ctrl.Result{}))
	})

	t.Run("removes finalizer cleanly when no labeled cluster resources exist", func(t *testing.T) {
		// W4c contract: if no ClusterRoles/CRDs/ClusterRoleBindings match the component label
		// (e.g. operator did not stamp the label), deleteClusterScopedResources still returns
		// nil and the finalizer is released — no panic, no error, no requeue.
		g := NewWithT(t)
		now := metav1.NewTime(time.Now())
		dep := &appsv1.Deployment{ObjectMeta: metav1.ObjectMeta{
			Name: depName, Namespace: depNS,
			DeletionTimestamp: &now,
			Finalizers:        []string{CleanupFinalizer},
		}}
		// No Tenant, no labeled ClusterRoles/CRDs/ClusterRoleBindings in the fake store.
		cli := fake.NewClientBuilder().WithScheme(selfDepScheme(t)).WithObjects(dep).Build()

		r := &LifecycleReconciler{Client: cli, DeploymentName: depName, DeploymentNS: depNS, TenantNamespace: tenantNS}
		res, err := r.Reconcile(t.Context(), req)
		g.Expect(err).ShouldNot(HaveOccurred())
		g.Expect(res).To(Equal(ctrl.Result{}))

		// Finalizer removed → fake client GCs the Deployment.
		var updated appsv1.Deployment
		getErr := cli.Get(t.Context(), req.NamespacedName, &updated)
		g.Expect(getErr).Should(HaveOccurred())
		g.Expect(getErr.Error()).To(ContainSubstring("not found"))
	})

 	t.Run("deletes Tenants then RBAC and CRDs when Deployment is terminating", func(t *testing.T) {
 		g := NewWithT(t)
 		now := metav1.NewTime(time.Now())