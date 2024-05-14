# Docs Agent chunking process

This page describes Docs Agent's chunking process and potential optimizations.

Currently, Docs Agent utilizes Markdown headings (`#`, `##`, and `###`) to
split documents into smaller, manageable chunks. However, the Docs Agent team
is actively developing more advanced strategies to improve the quality and
relevance of these chunks for retrieval.

## Chunking technique

In Retrieval Augmented Generation ([RAG][rag]) based systems, ensuring each
chunk contains the right information and context is crucial for accurate
retrieval. The goal of an effective chunking process is to ensure that each
chunk encapsulates a focused topic, which enhances the accuracy of retrieval
and ultimately leads to better answers. At the same time, the Docs Agent team
acknowledges the importance of a flexible approach that allows for
customization based on specific datasets and use cases.

Key characteristics in Docs Agent’s chunking process include:

- **Docs Agent splits documents based on Markdown headings.** However,
  this approach has limitations, especially when dealing with large sections.
- **Docs Agent chunks are smaller than 5000 bytes (characters).** This size
  limit is set by the embedding model used in generating embeddings.
- **Docs Agent enhances chunks with additional metadata.** The metadata helps
  Docs Agent to execute operations efficiently, such as preventing duplicate
  chunks in databases and deleting obsolete chunks that are  no longer
  present in the source.
- **Docs Agent retrieves the top 5 chunks and displays the top chunk's URL.**
  However, this is adjustable in Docs Agent’s configuration (see the `widget`
  and `experimental` app modes).

The Docs Agent team continues to explore various optimizations to enhance
the functionality and effectiveness of the chunking process. These efforts
include refining the chunking algorithm itself and developing advanced
post-processing techniques, for instance, reconstructing chunks to original
documents after retrieval.

Additionally, the team has been exploring methods for co-optimizing content
structure and chunking strategies, which aims to maximize retrieval
effectiveness by ensuring the structure of the source document itself
complements the chunking process.

## Chunks retrieval

Docs Agent employs two distinct approaches for storing and retrieving chunks:

- **The local database approach uses a [Chroma][chroma] vector database.**
  This approach grants greater control over the chunking and retrieval
  process. This option is recommended for development and experimental
  setups.
- **The online corpus approach uses Gemini’s
  [Semantic Retrieval API][semantic-retrieval].** This approach provides
  the advantages of centrally hosted online databases, ensuring
  accessibility for all users throughout the organization. This approach
  has some drawbacks, as control is reduced because the API may dictate
  how chunks are selected and where customization can be applied.

Choosing between these approaches depends on the specific needs of the user’s
deployment situation, which is to balance control and transparency against
possible improvements in performance, broader reach and ease of use.

<!-- Reference links -->

[rag]: concepts.md
[chroma]: https://docs.trychroma.com/
[semantic-retrieval]: https://ai.google.dev/gemini-api/docs/semantic_retrieval
