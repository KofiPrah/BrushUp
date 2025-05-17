# Recommended Workflow Configuration

To properly run the Art Critique application in Replit, update the workflow configuration:

1. Open `.replit` file in the Replit editor
2. Change the following line:
   ```
   args = "gunicorn --bind 0.0.0.0:5000 --certfile=cert.pem --keyfile=key.pem --reuse-port --reload main:app"
   ```
   
   To:
   ```
   args = "./run_app --http"
   ```

3. Set the environment variables:
   ```
   [env]
   SSL_ENABLED = "false"
   HTTP_ONLY = "true"
   ```

These changes ensure the application runs correctly with Replit's load balancer.