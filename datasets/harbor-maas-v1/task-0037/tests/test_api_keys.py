 
         cleanup_result = sp.run(
             ["oc", "exec", pod_name, "-n", deployment_namespace, "--",
             "curl", "-skf", "-X", "POST",
             "https://localhost:8443/internal/v1/api-keys/cleanup"],
             capture_output=True, text=True, timeout=30,
         )
 
         if cleanup_result.returncode != 0:
             # curl may not be available in the maas-api container; try wget
             cleanup_result = sp.run(
                 ["oc", "exec", pod_name, "-n", deployment_namespace, "--",
                 "wget", "-q", "--no-check-certificate", "-O-", "--post-data=",
                 "https://localhost:8443/internal/v1/api-keys/cleanup"],
                 capture_output=True, text=True, timeout=30,
             )
 