# Amazon Bedrock Knowledge Bases Chunking

When you ingest documents into an Amazon Bedrock Knowledge Base, the data is split into smaller pieces called chunks. This improves the speed and accuracy of retrieval. Bedrock offers several chunking strategies.

1.  **Fixed-size chunking:** This is the default option. The document is split into chunks of a specified maximum token size, with an optional overlap between adjacent chunks. This is a straightforward approach that works well for many document types.

2.  **Semantic chunking:** This strategy attempts to split the document along semantic boundaries. It uses a language model to find sentence groupings that are thematically related and creates chunks based on those groupings. This can result in more coherent and contextually complete chunks.

3.  **Hierarchical chunking:** For very large and structured documents, this strategy can be employed. It involves creating chunks of different sizes, often corresponding to the document's structure (e.g., paragraphs within sections within chapters). Smaller chunks are retrieved for precision, but can be mapped back to their larger parent chunks to provide more context to the language model.