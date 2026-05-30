# Amazon Titan Multimodal Embeddings

Amazon Titan Multimodal Embeddings G1 is a model that generates vector representations from text or images. The embeddings can be used for a variety of tasks, including search, recommendation, and classification.

**Input Modalities:** The model accepts two types of input:
1.  **Text:** A string of up to 8,192 tokens.
2.  **Image:** A base64-encoded image or an S3 object path.

When providing both an image and text, the model generates a single embedding that represents the combined semantic meaning of both inputs. This is useful for multimodal search applications where users can search for images using text queries or find similar images. The output embedding dimension is 1,024.