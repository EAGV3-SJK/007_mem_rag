# Amazon SageMaker Inference Options

Amazon SageMaker provides several options for deploying machine learning models for inference.

## Real-Time Inference

Real-Time Inference is designed for workloads that require low latency and high throughput. You provision dedicated instances that are always on and ready to serve requests.

- **Pricing Model:** You pay for the instances for as long as they are running, regardless of the number of requests.
- **Cold Starts:** There are no cold starts; the endpoint is always warm.
- **Use Case:** Suitable for production applications with consistent traffic, like a recommendation engine on an e-commerce site.

## Serverless Inference

Serverless Inference is designed for workloads with intermittent or unpredictable traffic. SageMaker automatically provisions, scales, and turns off compute resources based on the traffic.

- **Pricing Model:** You pay for the compute time used to process requests, measured in milliseconds, and the amount of data processed.
- **Cold Starts:** There can be a cold start latency for the first request after a period of inactivity as SageMaker provisions resources.
- **Use Case:** Suitable for development/testing, or applications with infrequent requests, like a chatbot that is only used during business hours.