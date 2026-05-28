 				"Should reject invalid ID: %s", tt.reason)
 			assert.NotEmpty(t, capturedID,
 				"Should generate new UUID for invalid ID")
 			// Verify it looks like a UUID (contains hyphens, right length)
 			assert.Contains(t, capturedID, "-",
 				"Generated ID should be UUID format")
			assert.Equal(t, capturedID, w.Header().Get("X-Request-ID"),
				"Response header should carry the generated (not the rejected) ID")
 		})
 	}
 }