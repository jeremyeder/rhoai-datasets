 	modelMgr, err := models.NewManager(testLogger, 15, "")
 	require.NoError(t, err)
 
	subscriptionSelector := subscription.NewSelector(testLogger, &fakeSubscriptionLister{}, lister)
 	modelsHandler := handlers.NewModelsHandler(testLogger, modelMgr, subscriptionSelector, lister)
 
 	config := fixtures.TestServerConfig{Objects: []runtime.Object{}}