 +-- kube-system (7 pods)                # Kubernetes core
 |
 +-- llm (0 pods, networking only)       # External model namespace
|   +-- ExternalModel: llm-katan-openai # -> 3-147-232-199.sslip.io (AWS, Let's Encrypt TLS)
 |   +-- ServiceEntry + DestinationRule  # Created by controller
 |   +-- HTTPRoute + AuthPolicy          # Created by controller
 |