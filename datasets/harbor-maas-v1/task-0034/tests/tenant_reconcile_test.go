 	apierrors "k8s.io/apimachinery/pkg/api/errors"
 	apimeta "k8s.io/apimachinery/pkg/api/meta"
 	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
 	"k8s.io/apimachinery/pkg/runtime"
 	"k8s.io/apimachinery/pkg/types"
 	utilruntime "k8s.io/apimachinery/pkg/util/runtime"
 	g.Expect(apierrors.IsNotFound(err)).To(BeTrue(), "tenant should be fully deleted after finalization")
 }
 
func TestTenantReconcile_DeletionCleansUpPersesResourcesByTrackingLabel(t *testing.T) {
	g := NewWithT(t)
	s := tenantTestScheme(t)

	const tenantNS = "models-as-a-service"
	const appNS = "opendatahub"
	now := metav1.NewTime(time.Now())
	tenant := &maasv1alpha1.Tenant{
		ObjectMeta: metav1.ObjectMeta{
			Name:              maasv1alpha1.TenantInstanceName,
			Namespace:         tenantNS,
			UID:               types.UID("tenant-uid"),
			DeletionTimestamp: &now,
			Finalizers:        []string{tenantFinalizer},
		},
	}

	dashboard := &unstructured.Unstructured{}
	dashboard.SetGroupVersionKind(tenantreconcile.GVKPersesDashboard)
	dashboard.SetName("dashboard-3-maas-usage-admin")
	dashboard.SetNamespace(appNS)
	dashboard.SetLabels(map[string]string{
		tenantreconcile.LabelTenantName:      tenant.Name,
		tenantreconcile.LabelTenantNamespace: tenant.Namespace,
	})

	datasource := &unstructured.Unstructured{}
	datasource.SetGroupVersionKind(tenantreconcile.GVKPersesDatasource)
	datasource.SetName("kuadrant-prometheus-datasource")
	datasource.SetNamespace(appNS)
	datasource.SetLabels(map[string]string{
		tenantreconcile.LabelTenantName:      tenant.Name,
		tenantreconcile.LabelTenantNamespace: tenant.Namespace,
	})

	cl := fake.NewClientBuilder().
		WithScheme(s).
		WithStatusSubresource(&maasv1alpha1.Tenant{}).
		WithObjects(tenant, dashboard, datasource).
		Build()

	r := &TenantReconciler{
		Client:            cl,
		Scheme:            s,
		OperatorNamespace: appNS,
		AppNamespace:      appNS,
		TenantNamespace:   tenantNS,
	}

	req := ctrl.Request{NamespacedName: types.NamespacedName{Name: tenant.Name, Namespace: tenantNS}}

	res1, err := r.Reconcile(context.Background(), req)
	g.Expect(err).NotTo(HaveOccurred())
	g.Expect(res1.RequeueAfter).To(Equal(finalizeRequeueInterval), "first pass issues child deletes and requeues")

	// Second reconcile: children are gone, finalizer removed.
	res2, err := r.Reconcile(context.Background(), req)
	g.Expect(err).NotTo(HaveOccurred())
	g.Expect(res2.RequeueAfter).To(BeNumerically("==", 0))

	// Verify Perses resources are deleted.
	dashList := &unstructured.UnstructuredList{}
	dashList.SetGroupVersionKind(tenantreconcile.GVKPersesDashboard)
	dashList.GetObjectKind().SetGroupVersionKind(tenantreconcile.GVKPersesDashboard.GroupVersion().WithKind("PersesDashboardList"))
	g.Expect(cl.List(context.Background(), dashList, client.InNamespace(appNS))).To(Succeed())
	g.Expect(dashList.Items).To(BeEmpty(), "PersesDashboard should be deleted by finalizer")

	dsList := &unstructured.UnstructuredList{}
	dsList.SetGroupVersionKind(tenantreconcile.GVKPersesDatasource)
	dsList.GetObjectKind().SetGroupVersionKind(tenantreconcile.GVKPersesDatasource.GroupVersion().WithKind("PersesDatasourceList"))
	g.Expect(cl.List(context.Background(), dsList, client.InNamespace(appNS))).To(Succeed())
	g.Expect(dsList.Items).To(BeEmpty(), "PersesDatasource should be deleted by finalizer")
}

 func TestTenantReconcile_NotFoundIsNoOp(t *testing.T) {
 	g := NewWithT(t)
 	s := tenantTestScheme(t)