# Amazon Bedrock Guardrails

Guardrails for Amazon Bedrock provides a way to implement safeguards for your generative AI applications. It helps ensure that responses are relevant, appropriate, and safe.

Guardrails are configured with a set of policies that are applied to both user prompts and model responses. These policies include:

1.  **Denied Topics:** You can define a set of topics that you want to prevent the model from discussing. For example, a banking assistant can be configured to avoid giving financial advice.

2.  **Content Filters:** You can configure filters for hate speech, insults, sexual content, and violence with different sensitivity levels. This allows you to control the safety of the model's replies.

3.  **Personally Identifiable Information (PII) Redaction:** Guardrails can detect and redact PII from the model's response, preventing sensitive data from being exposed.

4.  **Grounding:** You can configure the guardrail to check if the model's response is grounded in the provided source documents (from a knowledge base), reducing hallucinations.