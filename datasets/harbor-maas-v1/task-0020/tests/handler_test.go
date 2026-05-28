 	}
 }
 
func (m *mockAdminChecker) IsAdmin(_ context.Context, user *token.UserContext) (bool, error) {
 	if user == nil {
		return false, nil
 	}
 	for _, userGroup := range user.Groups {
 		if slices.Contains(m.adminGroups, userGroup) {
			return true, nil
 		}
 	}
	return false, nil
 }
 
 // executeSearchRequest is a test helper that executes a search request and returns the parsed response.
 
 	t.Run("OwnerCanAccess", func(t *testing.T) {
 		user := &token.UserContext{Username: "alice", Groups: []string{"users"}}
		result, err := h.isAuthorizedForKey(ctx, user, "alice")
		require.NoError(t, err)
		assert.True(t, result)
 	})
 
 	t.Run("NonOwnerCannotAccess", func(t *testing.T) {
 		user := &token.UserContext{Username: "bob", Groups: []string{"users"}}
		result, err := h.isAuthorizedForKey(ctx, user, "alice")
		require.NoError(t, err)
		assert.False(t, result)
 	})
 
 	t.Run("AdminCanAccessAnyKey", func(t *testing.T) {
 		admin := &token.UserContext{Username: "admin", Groups: []string{"admin-users"}}
		result, err := h.isAuthorizedForKey(ctx, admin, "alice")
		require.NoError(t, err)
		assert.True(t, result)
 	})
 }
 