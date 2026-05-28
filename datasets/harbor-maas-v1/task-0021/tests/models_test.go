 	defer cleanup()
 
 	// Create a mock subscription selector that auto-selects for single subscription users
	subscriptionSelector := subscription.NewSelector(testLogger, &fakeSubscriptionLister{}, nil)
 
 	modelsHandler := handlers.NewModelsHandler(testLogger, modelMgr, subscriptionSelector, maasModelRefLister)
 
 		"premium": []string{"premium-users"},
 		"free":    []string{"free-users"},
 	}
	subscriptionSelector := subscription.NewSelector(testLogger, multiSubLister, nil)
 
 	modelsHandler := handlers.NewModelsHandler(testLogger, modelMgr, subscriptionSelector, maasModelRefLister)
 	tokenHandler := token.NewHandler(testLogger, fixtures.TestTenant)
 	modelMgr, err := models.NewManager(testLogger, 15, "")
 	require.NoError(t, err)
 
	subscriptionSelector := subscription.NewSelector(testLogger, subscriptionLister, nil)
 	modelsHandler := handlers.NewModelsHandler(testLogger, modelMgr, subscriptionSelector, lister)
 
 	config := fixtures.TestServerConfig{Objects: []runtime.Object{}}
 			},
 		}
 
		subscriptionSelector := subscription.NewSelector(testLogger, emptySubscriptionLister, nil)
 		emptyHandler := handlers.NewModelsHandler(testLogger, modelMgr, subscriptionSelector, lister)
 
 		config := fixtures.TestServerConfig{Objects: []runtime.Object{}}
 	modelMgr, err := models.NewManager(testLogger, 15, "")
 	require.NoError(t, err)
 
	subscriptionSelector := subscription.NewSelector(testLogger, subscriptionLister, nil)
 	modelsHandler := handlers.NewModelsHandler(testLogger, modelMgr, subscriptionSelector, lister)
 
 	config := fixtures.TestServerConfig{Objects: []runtime.Object{}}
 	modelMgr, err := models.NewManager(testLogger, 15, "")
 	require.NoError(t, err)
 
	subscriptionSelector := subscription.NewSelector(testLogger, subscriptionLister, nil)
 	modelsHandler := handlers.NewModelsHandler(testLogger, modelMgr, subscriptionSelector, lister)
 
 	config := fixtures.TestServerConfig{Objects: []runtime.Object{}}
 	modelMgr, err := models.NewManager(testLogger, 15, "")
 	require.NoError(t, err)
 
	subscriptionSelector := subscription.NewSelector(testLogger, subscriptionLister, nil)
 	modelsHandler := handlers.NewModelsHandler(testLogger, modelMgr, subscriptionSelector, lister)
 
 	config := fixtures.TestServerConfig{Objects: []runtime.Object{}}
 	modelMgr, err := models.NewManager(testLogger, 15, "")
 	require.NoError(t, err)
 
	subscriptionSelector := subscription.NewSelector(testLogger, subscriptionLister, nil)
 	modelsHandler := handlers.NewModelsHandler(testLogger, modelMgr, subscriptionSelector, lister)
 
 	config := fixtures.TestServerConfig{Objects: []runtime.Object{}}