 	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
 
 	"github.com/opendatahub-io/models-as-a-service/maas-api/internal/logger"
	"github.com/opendatahub-io/models-as-a-service/maas-api/internal/models"
 	"github.com/opendatahub-io/models-as-a-service/maas-api/internal/subscription"
 	"github.com/opendatahub-io/models-as-a-service/maas-api/internal/token"
 )
 	router := gin.New()
 
 	log := logger.New(false)
	selector := subscription.NewSelector(log, lister, nil)
 	handler := subscription.NewHandler(log, selector)
 
 	router.POST("/subscriptions/select", handler.SelectSubscription)
 }
 
 func setupListTestRouter(lister subscription.Lister, username string, groups []string) *gin.Engine {
	return setupListTestRouterWithModels(lister, nil, username, groups)
}

func setupListTestRouterWithModels(lister subscription.Lister, modelLister models.MaaSModelRefLister, username string, groups []string) *gin.Engine {
 	gin.SetMode(gin.TestMode)
 	router := gin.New()
 
 	log := logger.New(false)
	selector := subscription.NewSelector(log, lister, modelLister)
 	handler := subscription.NewHandler(log, selector)
 
 	setUser := func(c *gin.Context) {
 	}
 }
 
// fakeModelLister implements models.MaaSModelRefLister for testing model ref enrichment.
type fakeModelLister struct {
	items []*unstructured.Unstructured
}

func (f *fakeModelLister) List() ([]*unstructured.Unstructured, error) {
	return f.items, nil
}

// createTestMaaSModelRef builds a fake MaaSModelRef unstructured object with display name and description annotations.
func createTestMaaSModelRef(name, namespace, displayName, description string) *unstructured.Unstructured {
	annotations := map[string]any{}
	if displayName != "" {
		annotations["openshift.io/display-name"] = displayName
	}
	if description != "" {
		annotations["openshift.io/description"] = description
	}
	return &unstructured.Unstructured{
		Object: map[string]any{
			"apiVersion": "maas.opendatahub.io/v1alpha1",
			"kind":       "MaaSModelRef",
			"metadata": map[string]any{
				"name":        name,
				"namespace":   namespace,
				"annotations": annotations,
			},
		},
	}
}

func TestListSubscriptions_ModelRefEnrichment(t *testing.T) {
	sub := createTestSubscriptionWithModels(
		"free-sub",
		[]string{"free-users"},
		[]struct{ ns, name string }{
			{ns: "llm-ns", name: "model-a"},
			{ns: "llm-ns", name: "model-b"},
		},
		10, "org-1", "cc-1",
	)

	subLister := &mockLister{subscriptions: []*unstructured.Unstructured{sub}}
	modelLister := &fakeModelLister{
		items: []*unstructured.Unstructured{
			createTestMaaSModelRef("model-a", "llm-ns", "Model A Display", "A great model"),
			createTestMaaSModelRef("model-b", "llm-ns", "Model B Display", ""),
		},
	}

	router := setupListTestRouterWithModels(subLister, modelLister, "alice", []string{"free-users"})
	req := httptest.NewRequest(http.MethodGet, "/v1/subscriptions", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Fatalf("expected status 200, got %d", w.Code)
	}

	var result []subscription.SubscriptionInfo
	if err := json.Unmarshal(w.Body.Bytes(), &result); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}
	if len(result) != 1 {
		t.Fatalf("expected 1 subscription, got %d", len(result))
	}

	refs := result[0].ModelRefs
	byName := make(map[string]subscription.ModelRefInfo, len(refs))
	for _, r := range refs {
		byName[r.Name] = r
	}

	// model-a has both display_name and description
	if byName["model-a"].DisplayName != "Model A Display" {
		t.Errorf("model-a: expected display_name %q, got %q", "Model A Display", byName["model-a"].DisplayName)
	}
	if byName["model-a"].Description != "A great model" {
		t.Errorf("model-a: expected description %q, got %q", "A great model", byName["model-a"].Description)
	}

	// model-b has a display_name but no description annotation
	if byName["model-b"].DisplayName != "Model B Display" {
		t.Errorf("model-b: expected display_name %q, got %q", "Model B Display", byName["model-b"].DisplayName)
	}
	if byName["model-b"].Description != "" {
		t.Errorf("model-b: expected empty description, got %q", byName["model-b"].Description)
	}
}

func TestListSubscriptions_ModelRefEnrichment_NilLister(t *testing.T) {
	sub := createTestSubscriptionWithAnnotations("free-sub", []string{"free-users"}, []string{"model-a"}, nil)
	subLister := &mockLister{subscriptions: []*unstructured.Unstructured{sub}}

	// nil model lister: enrichment is skipped, response must still succeed with empty display_name/description
	router := setupListTestRouterWithModels(subLister, nil, "alice", []string{"free-users"})
	req := httptest.NewRequest(http.MethodGet, "/v1/subscriptions", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Fatalf("expected status 200, got %d", w.Code)
	}

	var result []subscription.SubscriptionInfo
	if err := json.Unmarshal(w.Body.Bytes(), &result); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}
	if len(result) != 1 {
		t.Fatalf("expected 1 subscription, got %d", len(result))
	}
	for _, ref := range result[0].ModelRefs {
		if ref.DisplayName != "" || ref.Description != "" {
			t.Errorf("expected empty display_name and description with nil lister, got %q / %q", ref.DisplayName, ref.Description)
		}
	}
}

func TestListSubscriptions_ModelRefEnrichment_ModelNotFound(t *testing.T) {
	sub := createTestSubscriptionWithAnnotations("free-sub", []string{"free-users"}, []string{"unknown-model"}, nil)
	subLister := &mockLister{subscriptions: []*unstructured.Unstructured{sub}}
	// model lister does not contain "unknown-model"
	modelLister := &fakeModelLister{
		items: []*unstructured.Unstructured{
			createTestMaaSModelRef("other-model", "llm-ns", "Other Model", "Some description"),
		},
	}

	router := setupListTestRouterWithModels(subLister, modelLister, "alice", []string{"free-users"})
	req := httptest.NewRequest(http.MethodGet, "/v1/subscriptions", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Fatalf("expected status 200, got %d", w.Code)
	}

	var result []subscription.SubscriptionInfo
	if err := json.Unmarshal(w.Body.Bytes(), &result); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}
	if len(result) != 1 {
		t.Fatalf("expected 1 subscription, got %d", len(result))
	}
	for _, ref := range result[0].ModelRefs {
		if ref.DisplayName != "" || ref.Description != "" {
			t.Errorf("expected empty fields when model not found, got %q / %q", ref.DisplayName, ref.Description)
		}
	}
}

 func TestListSubscriptionsForModel_NoAccess(t *testing.T) {
 	lister := &mockLister{subscriptions: []*unstructured.Unstructured{
 		createTestSubscriptionWithAnnotations("premium-sub", []string{"premium-users"}, []string{"model-a"}, nil),