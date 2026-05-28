 	for _, tt := range tests {
 		t.Run(tt.name, func(t *testing.T) {
 			lister := &fakeLister{subscriptions: tt.subscriptions}
			selector := subscription.NewSelector(log, lister, nil)
 
 			result, err := selector.GetAllAccessible(tt.groups, tt.username)
 
 
 	t.Run("requires groups or username", func(t *testing.T) {
 		lister := &fakeLister{subscriptions: []*unstructured.Unstructured{}}
		selector := subscription.NewSelector(log, lister, nil)
 
 		_, err := selector.GetAllAccessible(nil, "")
 		if err == nil {
 			createSubscription("low-sub", []string{"g1"}, nil, 10, defaultTestTokenRateLimit, "L", "d1"),
 			createSubscription("high-sub", []string{"g1"}, nil, 50, defaultTestTokenRateLimit, "H", "d2"),
 		}}
		sel := subscription.NewSelector(log, lister, nil)
 		got, err := sel.SelectHighestPriority([]string{"g1"}, "")
 		if err != nil {
 			t.Fatalf("SelectHighestPriority: %v", err)
 			createSubscription("sub-a", []string{"g1"}, nil, 10, 10, "", ""),
 			createSubscription("sub-b", []string{"g1"}, nil, 10, 20, "", ""),
 		}}
		sel := subscription.NewSelector(log, lister, nil)
 		got, err := sel.SelectHighestPriority([]string{"g1"}, "")
 		if err != nil {
 			t.Fatalf("SelectHighestPriority: %v", err)
 			createSubscription("zebra", []string{"g1"}, nil, 5, defaultTestTokenRateLimit, "", ""),
 			createSubscription("alpha", []string{"g1"}, nil, 5, defaultTestTokenRateLimit, "", ""),
 		}}
		sel := subscription.NewSelector(log, lister, nil)
 		got, err := sel.SelectHighestPriority([]string{"g1"}, "")
 		if err != nil {
 			t.Fatalf("SelectHighestPriority: %v", err)
 		lister := &fakeLister{subscriptions: []*unstructured.Unstructured{
 			createSubscription("other", []string{"other-group"}, nil, 10, defaultTestTokenRateLimit, "", ""),
 		}}
		sel := subscription.NewSelector(log, lister, nil)
 		_, err := sel.SelectHighestPriority([]string{"g1"}, "")
 		if err == nil {
 			t.Fatal("expected error")
 	for _, tt := range tests {
 		t.Run(tt.name, func(t *testing.T) {
 			lister := &fakeLister{subscriptions: []*unstructured.Unstructured{tt.subscription}}
			selector := subscription.NewSelector(log, lister, nil)
 
 			//nolint:unqueryvet,nolintlint // False positive - not a SQL query
 			result, err := selector.Select([]string{"g1"}, "", "", "")
 	}
 
 	lister := &fakeLister{subscriptions: subscriptions}
	selector := subscription.NewSelector(log, lister, nil)
 
 	results, err := selector.GetAllAccessible([]string{"g1"}, "")
 	if err != nil {
 	for _, tt := range tests {
 		t.Run(tt.name, func(t *testing.T) {
 			lister := &fakeLister{subscriptions: []*unstructured.Unstructured{tt.subscription}}
			selector := subscription.NewSelector(log, lister, nil)
 
 			//nolint:unqueryvet,nolintlint // False positive - not a SQL query
 			result, err := selector.Select([]string{"g1"}, "", "", tt.requestedModel)