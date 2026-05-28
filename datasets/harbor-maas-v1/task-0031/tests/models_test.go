 		assert.True(t, subscriptionNames["sub-b"], "Should have model with sub-b")
 	})
 }

// maasModelRefExternalModelUnstructured creates a MaaSModelRef unstructured with kind=ExternalModel.
func maasModelRefExternalModelUnstructured(name, namespace, modelRefName string, ready bool, annotations map[string]string) *unstructured.Unstructured {
	u := &unstructured.Unstructured{}
	u.SetGroupVersionKind(schema.GroupVersionKind{
		Group:   maasModelRefGVRGroup,
		Version: maasModelRefGVRVersion,
		Kind:    "MaaSModelRef",
	})
	u.SetName(name)
	u.SetNamespace(namespace)
	u.SetCreationTimestamp(metav1.NewTime(time.Unix(1700000000, 0)))
	if ready {
		_ = unstructured.SetNestedField(u.Object, "Ready", "status", "phase")
	}
	_ = unstructured.SetNestedField(u.Object, "ExternalModel", "spec", "modelRef", "kind")
	_ = unstructured.SetNestedField(u.Object, modelRefName, "spec", "modelRef", "name")
	if len(annotations) > 0 {
		u.SetAnnotations(annotations)
	}
	return u
}

func TestListModels_ExternalModelUsesModelRefName(t *testing.T) {
	testLogger := logger.Development()

	const (
		maasModelRefName  = "friendly-alias"
		externalModelName = "gpt-4o-external"
	)

	lister := fakeMaaSModelRefLister{
		fixtures.TestNamespace: []*unstructured.Unstructured{
			maasModelRefExternalModelUnstructured(maasModelRefName, fixtures.TestNamespace, externalModelName, true, nil),
		},
	}

	modelMgr, err := models.NewManager(testLogger, 15, "")
	require.NoError(t, err)

	subscriptionSelector := subscription.NewSelector(testLogger, &fakeSubscriptionLister{})
	modelsHandler := handlers.NewModelsHandler(testLogger, modelMgr, subscriptionSelector, lister)

	config := fixtures.TestServerConfig{Objects: []runtime.Object{}}
	router, _ := fixtures.SetupTestServer(t, config)

	_, cleanup := fixtures.StubTokenProviderAPIs(t)
	defer cleanup()

	tokenHandler := token.NewHandler(testLogger, fixtures.TestTenant)
	v1 := router.Group("/v1")
	v1.GET("/models", tokenHandler.ExtractUserInfo(), modelsHandler.ListLLMs)

	w := httptest.NewRecorder()
	req, err := http.NewRequestWithContext(t.Context(), http.MethodGet, "/v1/models", nil)
	require.NoError(t, err)

	req.Header.Set("Authorization", "Bearer valid-token")
	req.Header.Set(constant.HeaderUsername, "test-user@example.com")
	req.Header.Set(constant.HeaderGroup, `["free-users"]`)
	router.ServeHTTP(w, req)

	require.Equal(t, http.StatusOK, w.Code)

	var response pagination.Page[models.Model]
	err = json.Unmarshal(w.Body.Bytes(), &response)
	require.NoError(t, err)

	require.Len(t, response.Data, 1, "Should return the ExternalModel")
	assert.Equal(t, externalModelName, response.Data[0].ID,
		"Model ID should be the ExternalModel name, not the MaaSModelRef name")
	assert.Equal(t, "ExternalModel", response.Data[0].Kind)
	assert.Equal(t, fixtures.TestNamespace+"/"+maasModelRefName, response.Data[0].OwnedBy,
		"OwnedBy should still reference the MaaSModelRef for dashboard display")
}