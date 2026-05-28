 
 	redacted := logger.RedactHeaders(headers, false)
 
	// Sensitive headers should be redacted (using canonical keys)
 	assert.Equal(t, "present", redacted["Authorization"],
 		"Authorization should be redacted")
	assert.Equal(t, "present", redacted["X-Api-Key"],
 		"X-API-Key should be redacted")
 
	// Non-sensitive headers should pass through (using canonical keys)
 	assert.Equal(t, "application/json", redacted["Content-Type"],
 		"Content-Type should pass through")
	assert.Equal(t, "abc-123", redacted["X-Request-Id"],
 		"X-Request-ID should pass through")
	assert.Equal(t, "user@example.com", redacted["X-Maas-Username"],
 		"X-MaaS-Username should pass through")
 }
 
 		"Non-sensitive header should pass through")
 }
 
func TestSensitiveHeadersSummaryForAccessLog(t *testing.T) {
	h := http.Header{}
	h.Set("Authorization", "Bearer secret")
	h.Set("Cookie", "session=abc")

	summary := logger.SensitiveHeadersSummaryForAccessLog(h)
	assert.Contains(t, summary, "Authorization=present")
	assert.NotContains(t, summary, "secret")
	assert.NotContains(t, summary, "session=abc")
}

 func TestIsSensitiveHeader_CaseInsensitive(t *testing.T) {
 	tests := []struct {
 		name      string