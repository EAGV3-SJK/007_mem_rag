

# Model Context Protocol strategies on AWS
<a name="introduction"></a>

*Amazon Web Services* ([contributors](contributors.md))

*March 2026* ([document history](doc-history.md))

This guide can help you develop and implement Model Context Protocol (MCP) strategies across your organization to support your agentic AI journey. As agents and language models become increasingly central to business operations, establishing an MCP strategy is critical for successful agentic solutions.

This guide explores three foundational pillars for building an MCP strategy: MCP tool design, MCP server hosting, and MCP governance. By addressing these interconnected components, organizations can create scalable, secure, and effective systems for managing model context across their AI implementations. This guidance provides actionable insights and strategic guidance for organizations at any stage of an organization's AI journey, from initial experimentation to full-scale production deployments. This helps them develop tailored MCP solutions that align with their specific needs and objectives.

These best practices are derived from real-world implementations of organizations deploying MCP at enterprise scale, an analysis of current MCP specification standards, and lessons learned from custom Large Language Model (LLM) applications in production.

AI systems use increasingly sophisticated and robust LLMs in a wide variety of use cases. LLMs excel at understanding natural language, generating human-like responses, and reasoning over complex information. However, to transform LLMs from conversational interfaces into systems that can autonomously accomplish complex tasks, organizations are adopting *agentic AI architectures*, AI systems that can perceive their environment, reason about goals, make autonomous decisions, orchestrate across multiple steps, and take actions to achieve objectives on behalf of users. This agentic approach helps organizations build AI systems that can understand user intent through natural language, autonomously coordinate across multiple data sources and tools, and deliver personalized experiences at a scale that was not possible with traditional request-response patterns. To make these agents more capable, organizations need to provide access to their existing tools and data to enrich the agent's contextual understanding and allow it to act on a user's behalf.

[MCP](https://modelcontextprotocol.io/) provides a standardized protocol for AI-tool integration, enabling consistent communication between agents and external resources. While MCP itself defines the communication standard, implementing it effectively requires careful consideration of architectural patterns, security models, operational practices, and performance optimization strategies to achieve scalable, secure, and maintainable solutions.

This guide synthesizes lessons learned from enterprise MCP deployments, providing actionable recommendations that align with the [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/). It covers strategies for MCP tool design, MCP server hosting, and MCP governance, which are essential in building your own MCP solutions. The recommendations in this guide map to the following five pillars of the AWS Well-Architected Framework:
+ **Security** – Token isolation, scoped-down credentials, separate read/write authorization
+ **Operational Excellence** – Tool selection accuracy metrics, golden datasets for regression testing
+ **Reliability** – Per-user and per-tool rate limiting, load shedding
+ **Performance efficiency** – Workflow-scoped tools, tool filtering, semantic search to reduce context window usage
+ **Cost optimization** – Reusable MCP servers across teams, reduced per-request token costs through tool filtering

## Intended audience
<a name="intended-audience"></a>

This guide is intended for architects, developers, and technology leaders who are implementing agentic AI solutions in their organizations. To understand the concepts in this guide, you should understand how LLMs work and have foundational knowledge about MCP, tools, and prompt engineering.

## Objectives
<a name="objectives"></a>

Building Agentic AI systems that are production-ready means solving for governance, optimization, and security together to support your organization's policies. The below explains how this guide addresses these objectives:
+ **Governance** – Without centralized governance, you cannot answer audit questions about your AI workloads, including which agents accessed which data, with what permissions, and when. You also cannot enforce versioning. The [MCP hosting strategy](mcp-hosting-strategy.md) section of this guide explains how users could be running outdated local MCP servers with known vulnerabilities due to lack of systematic enforcements.

  For regulated industries, governance is critical. Auditors want to see policy enforcement and tool usage tracking across all agents from a single pane. MCP governance provides that.

  By following the recommendations in this guide, you can improve task accuracy by 28-32% in peer-reviewed benchmarks. For more information, see [MARCO: Multi-Agent Real-time Chat Orchestration](https://aclanthology.org/2024.emnlp-industry.102/) (ACL Anthology website). Governance is not just about compliance; it also improves your agentic AI system performance.
+ **Optimization** – Your teams might build the same integrations more than once. For example, when five different teams write their own database query script for their AI application to communicate with their databases, that's five times the development cost and five sets of bugs list to maintain. MCP lets you build it once and share it across the entire engineering community. The savings compound as your agent count grows.

  There is also a per-request cost problem that most teams don't notice at first. Every tool definition consumes context window tokens. At 20 tools, you're spending 5,000-10,000 tokens per invocation on descriptions alone, alongside the user inquiries. This increases latency and LLM inference costs and degrades accuracy as the model struggles to pick the right tool from the list of available tools.

  Agents that use structured tool wrappers are approximately three times more accurate on database tasks than agents that access APIs directly (for more information, see [Middleware for LLMs: Tools Are Instrumental for Language Agents in Complex Environments](https://aclanthology.org/2024.emnlp-main.436.pdf)). How you design and present tools to an AI model is important. This guide recommends giving tools clear schemas, scoping them to actual workflows instead of raw endpoints, and limiting information in the context window. The [MCP tool design strategy](mcp-tool-strategy.md) section of this guide dives deep into these aspects.
+ **Security and compliance** – Imagine an agentic AI system that hallucinates a cleanup step and tries to delete a production database. If the agent inherited the user's full admin credentials, the deletion might go through. With token isolation and scoped-down credentials that only grant read and create access, it fails safely.

  Regulated workflows sharpen this further. The guide provides examples (healthcare pipelines that require HIPAA validation and personally identifiable information anonymization before processing patient data). Embedding such logic in MCP tools means compliance happens deterministically every time.