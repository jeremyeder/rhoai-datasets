 	})
 }
 
func TestSearchAPIKeys_SubscriptionFilter(t *testing.T) {
	gin.SetMode(gin.TestMode)
	store := NewMockStore()
	cfg := &config.Config{}
	service := NewServiceWithLogger(store, cfg, fixedSubSelector{}, logger.Development())
	handler := NewHandler(logger.Development(), service, newMockAdminChecker())

	ctx := context.Background()
	testUser := &token.UserContext{
		Username: "test-user",
		Groups:   []string{"system:authenticated"},
	}

	err := store.AddKey(ctx, testUser.Username, "key-sub-a", "hash-a", "Key A", "", []string{"system:authenticated"}, "subscription-a", nil, false)
	require.NoError(t, err)
	err = store.AddKey(ctx, testUser.Username, "key-sub-b", "hash-b", "Key B", "", []string{"system:authenticated"}, "subscription-b", nil, false)
	require.NoError(t, err)

	t.Run("FilterBySubscription", func(t *testing.T) {
		requestBody := `{"filters": {"subscription": "subscription-a"}}`

		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		c.Request = httptest.NewRequest(http.MethodPost, "/v1/api-keys/search", nil)
		c.Request.Header.Set("Content-Type", "application/json")
		c.Request.Body = io.NopCloser(strings.NewReader(requestBody))
		c.Set("user", testUser)

		handler.SearchAPIKeys(c)

		assert.Equal(t, http.StatusOK, w.Code)
		var response SearchAPIKeysResponse
		err := json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Len(t, response.Data, 1)
		assert.Equal(t, "subscription-a", response.Data[0].Subscription)
	})

	t.Run("NoFilterReturnsAll", func(t *testing.T) {
		requestBody := `{}`

		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		c.Request = httptest.NewRequest(http.MethodPost, "/v1/api-keys/search", nil)
		c.Request.Header.Set("Content-Type", "application/json")
		c.Request.Body = io.NopCloser(strings.NewReader(requestBody))
		c.Set("user", testUser)

		handler.SearchAPIKeys(c)

		assert.Equal(t, http.StatusOK, w.Code)
		var response SearchAPIKeysResponse
		err := json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Len(t, response.Data, 2, "should return all keys when no subscription filter")
	})
}

 func TestSearchAPIKeys_Sorting(t *testing.T) {
 	gin.SetMode(gin.TestMode)
 	store := NewMockStore()