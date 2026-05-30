"""
build_corpus.py

Creates the full RAG corpus, including documents on AWS AI services and
Constraint Programming. This script generates the ground truth documents
for the five queries specified in `aws_queries.json`.

Run once from the `007_mem_rag` directory:
  python scripts/build_corpus.py
"""
from pathlib import Path

ROOT = Path(__file__).parent.parent / "corpus"

FILES: dict[str, str] = {
    # ── Queries Q1-Q5 Ground Truth (AWS AI Services) ────────────────────────
    "aws/amazon-titan-multimodal-embeddings.md": """# Amazon Titan Multimodal Embeddings

Amazon Titan Multimodal Embeddings G1 is a model that generates vector representations from text or images. The embeddings can be used for a variety of tasks, including search, recommendation, and classification.

**Input Modalities:** The model accepts two types of input:
1.  **Text:** A string of up to 8,192 tokens.
2.  **Image:** A base64-encoded image or an S3 object path.

When providing both an image and text, the model generates a single embedding that represents the combined semantic meaning of both inputs. This is useful for multimodal search applications where users can search for images using text queries or find similar images. The output embedding dimension is 1,024.
""",
    "aws/sagemaker-inference-options.md": """# Amazon SageMaker Inference Options

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
""",
    "aws/bedrock-knowledge-bases.md": """# Amazon Bedrock Knowledge Bases Chunking

When you ingest documents into an Amazon Bedrock Knowledge Base, the data is split into smaller pieces called chunks. This improves the speed and accuracy of retrieval. Bedrock offers several chunking strategies.

1.  **Fixed-size chunking:** This is the default option. The document is split into chunks of a specified maximum token size, with an optional overlap between adjacent chunks. This is a straightforward approach that works well for many document types.

2.  **Semantic chunking:** This strategy attempts to split the document along semantic boundaries. It uses a language model to find sentence groupings that are thematically related and creates chunks based on those groupings. This can result in more coherent and contextually complete chunks.

3.  **Hierarchical chunking:** For very large and structured documents, this strategy can be employed. It involves creating chunks of different sizes, often corresponding to the document's structure (e.g., paragraphs within sections within chapters). Smaller chunks are retrieved for precision, but can be mapped back to their larger parent chunks to provide more context to the language model.
""",
    "aws/amazon-q-quicksight.md": """# Amazon Q in QuickSight

Amazon Q in QuickSight enhances Business Intelligence (BI) by allowing users to query their data using natural language. It bridges the gap between complex BI tools and business users who need fast answers from their datasets.

Users can ask questions like "what were the top 10 products by sales last quarter?" and Amazon Q will generate a visual answer, such as a bar chart, along with a narrative summary. It can build dashboards, create calculations, and generate insights without requiring the user to write any SQL or manually configure charts.

The feature is powered by a large language model trained on a vast amount of SQL, BI dashboard structures, and natural language. It interprets the user's intent, maps it to the underlying dataset schema, and generates the appropriate SQL generation or visualization configuration.
""",
    "aws/bedrock-guardrails.md": """# Amazon Bedrock Guardrails

Guardrails for Amazon Bedrock provides a way to implement safeguards for your generative AI applications. It helps ensure that responses are relevant, appropriate, and safe.

Guardrails are configured with a set of policies that are applied to both user prompts and model responses. These policies include:

1.  **Denied Topics:** You can define a set of topics that you want to prevent the model from discussing. For example, a banking assistant can be configured to avoid giving financial advice.

2.  **Content Filters:** You can configure filters for hate speech, insults, sexual content, and violence with different sensitivity levels. This allows you to control the safety of the model's replies.

3.  **Personally Identifiable Information (PII) Redaction:** Guardrails can detect and redact PII from the model's response, preventing sensitive data from being exposed.

4.  **Grounding:** You can configure the guardrail to check if the model's response is grounded in the provided source documents (from a knowledge base), reducing hallucinations.
""",

    # ── Constraint Programming Docs ─────────────────────────────────────────
    "constraint-programming/cp-overview.md": """# Constraint Programming (CP) Overview

Constraint Programming is a paradigm for solving combinatorial problems that works by stating constraints (properties) of a solution and then finding a solution that satisfies all constraints. It is particularly effective for problems in areas like scheduling, planning, and resource allocation.

A CP problem is defined by:
1.  **Variables:** A set of decision variables, each with a domain of possible values (e.g., an integer range, a set of categories).
2.  **Constraints:** A set of relationships between variables that restrict the values they can take simultaneously.

A CP solver explores the search space of possible variable assignments, systematically eliminating values that violate constraints. This process, called **propagation**, reduces the domains of variables. When propagation stops, the solver makes a choice (branching) to assign a value to a variable and repeats the process until a solution is found or the search space is exhausted.

Unlike traditional optimization methods that rely on a single objective function (like Linear Programming), CP excels at finding *feasible* solutions in highly constrained search spaces.
""",
    "constraint-programming/cp-vs-optimization.md": """# Constraint Programming vs. Mathematical Optimization

Constraint Programming (CP) and Mathematical Optimization (like Linear Programming - LP, or Mixed-Integer Programming - MIP) are both used to solve complex decision-making problems, but they approach it differently.

**Mathematical Optimization (LP/MIP):**
- **Focus:** Finding the *optimal* solution for a single objective function (e.g., minimize cost, maximize profit).
- **Structure:** Problems are defined by linear or integer variables, linear constraints (equalities/inequalities), and an objective function.
- **Strengths:** Very efficient for problems that fit the linear model. Solvers like Gurobi or CPLEX can handle millions of variables.
- **Weaknesses:** Less effective for problems with arbitrary or logical constraints (e.g., "if task A is assigned to machine 1, then task B cannot be").

**Constraint Programming (CP):**
- **Focus:** Finding a *feasible* solution that satisfies a wide range of complex, often logical, constraints. Optimization is often secondary.
- **Structure:** Problems are defined by variables with domains and arbitrary constraints (e.g., `alldifferent`, logical implications).
- **Strengths:** Highly expressive. Excellent for scheduling, timetabling, and sequencing problems where the constraints are complex and non-linear.
- **Weaknesses:** Can be slower than MIP solvers on problems that have a strong linear structure.

In practice, many problems benefit from a hybrid approach, combining techniques from both fields. For example, a CP model might be used to find a feasible schedule, and an LP model might be used to optimize costs within that schedule.
""",
    "constraint-programming/aws-for-cp.md": """# Using AWS for Constraint Programming

While AWS does not offer a dedicated "Constraint Programming as a Service," its cloud infrastructure is an excellent platform for running CP solvers at scale.

**1. Compute with Amazon EC2:**
CP solvers can be computationally intensive. You can run open-source solvers (like Google OR-Tools, Choco, or MiniZinc) or commercial solvers (like IBM CPLEX or Gurobi) on powerful Amazon EC2 instances. Using Spot Instances can significantly reduce the cost of large-scale batch solving.

**2. Orchestration with AWS Step Functions:**
Many real-world CP problems are part of a larger workflow. For example, a vehicle routing problem might require fetching order data, running the solver, and then dispatching routes to drivers. AWS Step Functions can orchestrate this entire process, managing dependencies, retries, and error handling. A Step Function can trigger a solver running in an AWS Lambda function (for short-lived problems) or on an EC2 instance/ECS task via AWS Batch (for long-running problems).

**3. Serverless Solving with AWS Lambda:**
For smaller CP problems that can be solved within Lambda's 15-minute execution limit, you can package a solver library (like OR-Tools) into a Lambda layer and invoke it via an API Gateway endpoint or other event source. This provides a cost-effective, pay-per-use model for on-demand solving.

**4. Data Storage and Integration:**
Input data for CP models (e.g., job durations, machine availability, order locations) can be stored in Amazon S3, Amazon DynamoDB, or Amazon RDS, and fed into the solver at runtime.
""",
    "constraint-programming/or-tools.md": """# Introduction to Google OR-Tools

Google OR-Tools is a popular open-source software suite for solving combinatorial optimization problems. It is written in C++ but provides wrappers for Python, Java, and .NET.

OR-Tools is not a single solver but a collection of them, including:
- **CP-SAT Solver:** The primary constraint programming solver in the suite. It is a powerful and modern solver that combines techniques from Constraint Programming (CP) and Satisfiability (SAT). It is particularly strong on scheduling and routing problems.
- **Linear and Mixed-Integer Programming Solvers:** OR-Tools includes its own LP/MIP solver (Glop) and provides a unified interface to commercial solvers like Gurobi and CPLEX, and open-source ones like SCIP.
- **Routing Library:** A specialized library for solving Vehicle Routing Problems (VRP) and Traveling Salesperson Problems (TSP).

The CP-SAT solver is the highlight for constraint programming. A typical workflow in Python involves:
1.  Creating a `CpModel` instance.
2.  Defining variables with their domains (e.g., `model.NewIntVar(...)`).
3.  Adding constraints to the model (e.g., `model.AddAllDifferent(...)`, `model.Add(...)`).
4.  Optionally defining an objective to minimize or maximize.
5.  Creating a `CpSolver` instance and calling `solver.Solve(model)`.
6.  Interpreting the results and retrieving the values of the variables.

Because of its permissive Apache 2.0 license and strong performance, OR-Tools has become a standard choice for developers building applications that require solving optimization problems.
""",
    "constraint-programming/cp-use-cases.md": """# Use Cases for Constraint Programming

Constraint Programming (CP) is highly effective for a class of problems characterized by complex logical relationships and combinatorial search spaces. Common use cases include:

**1. Employee Scheduling and Rostering:**
Assigning staff to shifts while respecting constraints like:
- Each employee must work between 3 and 5 shifts per week.
- No employee can work more than 8 hours in a day.
- At least two senior employees must be on every shift.
- Alice and Bob cannot be scheduled on the same day.

**2. Vehicle Routing Problem (VRP):**
Finding the optimal set of routes for a fleet of vehicles to serve a set of customers. Constraints can include vehicle capacity, time windows for deliveries, and driver work-hour limits.

**3. Job Shop Scheduling:**
Scheduling a set of jobs on a set of machines, where each job consists of a sequence of tasks. Constraints include task precedence (task A must finish before task B starts) and resource constraints (a machine can only process one task at a time).

**4. University Timetabling:**
Assigning courses to classrooms and time slots while avoiding conflicts. Constraints include:
- A professor cannot teach two courses at the same time.
- A classroom cannot host two courses at the same time.
- The number of students enrolled in a course cannot exceed the classroom's capacity.

**5. Configuration Problems:**
Helping users configure a complex product (like a car or a computer) by ensuring that their choices are compatible. For example, selecting a certain engine might require selecting a specific transmission.
""",

    # ── Filler Docs (AWS General) to reach 50+ ──────────────────────────────
    "aws/aws-lambda.md": "# AWS Lambda\nAWS Lambda is a serverless compute service that runs your code in response to events.",
    "aws/amazon-s3.md": "# Amazon S3\nAmazon Simple Storage Service (S3) is an object storage service.",
    "aws/amazon-ec2.md": "# Amazon EC2\nAmazon Elastic Compute Cloud (EC2) provides scalable virtual servers.",
    "aws/amazon-dynamodb.md": "# Amazon DynamoDB\nA fully managed NoSQL database service.",
    "aws/amazon-rds.md": "# Amazon RDS\nAmazon Relational Database Service (RDS) is a managed relational database service.",
    "aws/aws-iam.md": "# AWS IAM\nAWS Identity and Access Management (IAM) manages access to AWS services.",
    "aws/amazon-vpc.md": "# Amazon VPC\nAmazon Virtual Private Cloud (VPC) lets you provision a logically isolated section of the AWS Cloud.",
    "aws/aws-cloudformation.md": "# AWS CloudFormation\nAn infrastructure as code service for provisioning AWS resources.",
    "aws/amazon-route53.md": "# Amazon Route 53\nA scalable Domain Name System (DNS) web service.",
    "aws/amazon-api-gateway.md": "# Amazon API Gateway\nA fully managed service for creating, publishing, and securing APIs.",
    "aws/aws-sdk.md": "# AWS SDK\nSoftware Development Kits for various languages to interact with AWS services.",
    "aws/aws-cli.md": "# AWS CLI\nA unified tool to manage your AWS services from the command line.",
    "aws/amazon-cloudwatch.md": "# Amazon CloudWatch\nA monitoring and observability service.",
    "aws/aws-eventbridge.md": "# AWS EventBridge\nA serverless event bus that connects application data from various sources.",
    "aws/aws-step-functions.md": "# AWS Step Functions\nA serverless function orchestrator for sequencing Lambda functions.",
    "aws/amazon-sqs.md": "# Amazon SQS\nAmazon Simple Queue Service (SQS) is a fully managed message queuing service.",
    "aws/amazon-sns.md": "# Amazon SNS\nAmazon Simple Notification Service (SNS) is a managed service for sending notifications.",
    "aws/aws-kms.md": "# AWS KMS\nAWS Key Management Service (KMS) makes it easy to create and manage cryptographic keys.",
    "aws/aws-secrets-manager.md": "# AWS Secrets Manager\nHelps you protect secrets needed to access your applications, services, and IT resources.",
    "aws/amazon-efs.md": "# Amazon EFS\nAmazon Elastic File System (EFS) provides a simple, scalable, elastic file system.",
    "aws/amazon-fsx.md": "# Amazon FSx\nA fully managed third-party file system service.",
    "aws/aws-backup.md": "# AWS Backup\nA centralized backup service.",
    "aws/aws-glue.md": "# AWS Glue\nA serverless data integration service for ETL jobs.",
    "aws/amazon-athena.md": "# Amazon Athena\nAn interactive query service that makes it easy to analyze data in Amazon S3 using standard SQL.",
    "aws/amazon-redshift.md": "# Amazon Redshift\nA fully managed, petabyte-scale data warehouse service.",
    "aws/amazon-kinesis.md": "# Amazon Kinesis\nCollect, process, and analyze real-time, streaming data.",
    "aws/aws-dms.md": "# AWS DMS\nAWS Database Migration Service helps you migrate databases to AWS easily and securely.",
    "aws/sagemaker-studio.md": "# SageMaker Studio\nAn IDE for machine learning.",
    "aws/sagemaker-autopilot.md": "# SageMaker Autopilot\nAutomatically builds, trains, and tunes the best machine learning models.",
    "aws/sagemaker-jumpstart.md": "# SageMaker JumpStart\nProvides pre-trained models and solution templates.",
    "aws/sagemaker-pipelines.md": "# SageMaker Pipelines\nCI/CD service for machine learning.",
    "aws/sagemaker-feature-store.md": "# SageMaker Feature Store\nA fully managed repository for ML features.",
    "aws/sagemaker-data-wrangler.md": "# SageMaker Data Wrangler\nReduces the time it takes to aggregate and prepare data for ML.",
    "aws/bedrock-agents.md": "# Agents for Amazon Bedrock\nCreate fully managed agents that perform tasks.",
    "aws/bedrock-models.md": "# Foundation Models in Bedrock\nAccess to foundation models from AI21 Labs, Anthropic, Cohere, Meta, and Amazon.",
    "aws/titan-text.md": "# Amazon Titan Text\nLarge language models for text generation.",
    "aws/titan-image-generator.md": "# Amazon Titan Image Generator\nGenerate realistic images from text.",
    "aws/aws-comprehend.md": "# Amazon Comprehend\nA natural language processing (NLP) service.",
    "aws/aws-translate.md": "# Amazon Translate\nA neural machine translation service.",
    "aws/aws-polly.md": "# Amazon Polly\nA service that turns text into lifelike speech.",
    "aws/aws-rekognition.md": "# Amazon Rekognition\nImage and video analysis service.",
    "aws/aws-textract.md": "# Amazon Textract\nAutomatically extracts text and data from scanned documents.",
    "aws/aws-lex.md": "# Amazon Lex\nA service for building conversational interfaces.",
    "aws/aws-forecast.md": "# Amazon Forecast\nA fully managed service that uses machine learning to deliver highly accurate forecasts.",
    "aws/aws-personalize.md": "# Amazon Personalize\nA machine learning service to create real-time personalized recommendations.",
    "aws/aws-codecommit.md": "# AWS CodeCommit\nA fully-managed source control service.",
    "aws/aws-codebuild.md": "# AWS CodeBuild\nA fully managed continuous integration service.",
    "aws/aws-codedeploy.md": "# AWS CodeDeploy\nA service that automates code deployments.",
    "aws/aws-codepipeline.md": "# AWS CodePipeline\nA fully managed continuous delivery service.",
    "aws/aws-xray.md": "# AWS X-Ray\nHelps developers analyze and debug distributed applications.",
}


def main() -> None:
    """Writes the corpus files to the corpus/ directory."""
    ROOT.mkdir(parents=True, exist_ok=True)
    count = 0
    for rel_path, content in FILES.items():
        path = ROOT / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip(), encoding="utf-8")
        words = len(content.split())
        print(f"  Wrote {path}  ({words} words)")
        count += 1
    print(f"\nTotal files written: {count}")


if __name__ == "__main__":
    main()