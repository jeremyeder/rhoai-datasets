 		checker := auth.NewSARAdminChecker(client, testNamespace)
 		user := &token.UserContext{Username: "admin-user", Groups: []string{"admin-group"}}
 
		result, err := checker.IsAdmin(context.Background(), user)
		require.NoError(t, err)
		assert.True(t, result)
 	})
 
 	t.Run("RegularUserDenied", func(t *testing.T) {
 		checker := auth.NewSARAdminChecker(client, testNamespace)
 		user := &token.UserContext{Username: "regular-user", Groups: []string{"users"}}
 
		result, err := checker.IsAdmin(context.Background(), user)
		require.NoError(t, err)
		assert.False(t, result)
 	})
 
 	t.Run("NilUserReturnsFalse", func(t *testing.T) {
 		client := fake.NewSimpleClientset()
 		checker := auth.NewSARAdminChecker(client, testNamespace)
 
		result, err := checker.IsAdmin(context.Background(), nil)
		require.NoError(t, err)
		assert.False(t, result)
 	})
 
 	t.Run("EmptyUsernameReturnsFalse", func(t *testing.T) {
 		client := fake.NewSimpleClientset()
 		checker := auth.NewSARAdminChecker(client, testNamespace)
 		user := &token.UserContext{Username: "", Groups: []string{"admin-group"}}
 
		result, err := checker.IsAdmin(context.Background(), user)
		require.NoError(t, err)
		assert.False(t, result)
 	})
 
 	t.Run("NilCheckerReturnsFalse", func(t *testing.T) {
 		var checker *auth.SARAdminChecker
 		user := &token.UserContext{Username: "admin-user", Groups: []string{"admin-group"}}
 
		result, err := checker.IsAdmin(context.Background(), user)
		require.NoError(t, err)
		assert.False(t, result)
 	})
 
 	t.Run("NilClientPanics", func(t *testing.T) {
 		})
 	})
 
	t.Run("APIErrorReturnsError", func(t *testing.T) {
 		client := fake.NewSimpleClientset()
 		client.PrependReactor("create", "subjectaccessreviews", func(action k8stesting.Action) (bool, runtime.Object, error) {
 			return true, nil, assert.AnError
 		checker := auth.NewSARAdminChecker(client, testNamespace)
 		user := &token.UserContext{Username: "admin-user", Groups: []string{"admin-group"}}
 
		result, err := checker.IsAdmin(context.Background(), user)
		assert.False(t, result, "should fail-closed on API error")
		assert.Error(t, err, "should return error on API failure")
 	})
 
 	t.Run("VerifiesSARParameters", func(t *testing.T) {
 		checker := auth.NewSARAdminChecker(client, testNamespace)
 		user := &token.UserContext{Username: "alice", Groups: []string{"group1", "group2"}}
 
		_, err := checker.IsAdmin(context.Background(), user)
		require.NoError(t, err)
 
 		require.NotNil(t, capturedSAR)
 		assert.Equal(t, "alice", capturedSAR.Spec.User)
 		checker := auth.NewSARAdminChecker(client, "custom-namespace")
 		user := &token.UserContext{Username: "alice", Groups: []string{"users"}}
 
		_, err := checker.IsAdmin(context.Background(), user)
		require.NoError(t, err)
 
 		require.NotNil(t, capturedSAR)
 		assert.Equal(t, "custom-namespace", capturedSAR.Spec.ResourceAttributes.Namespace)