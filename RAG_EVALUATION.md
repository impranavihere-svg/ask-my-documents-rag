# RAG Evaluation

## Test Document

Module1.pdf – Agentic AI Software Development

## Evaluation Questions

| Test | Question | Expected Answer | Retrieved Context | Generated Answer | Grounded? |
|---|---|---|---|---|---|
| 1. Present | What is Generative AI? | Explain Generative AI using the uploaded document. | Relevant chunks about Generative AI | Answer generated from document | Yes |
| 2. Two-part | What is Agentic AI and what are its characteristics? | Give the definition and characteristics of Agentic AI. | Relevant chunks about Agentic AI | Answer generated from document | Yes |
| 3. Absent | Who won the FIFA World Cup in 2030? | Information should be unavailable in the uploaded document. | Retrieved chunks do not contain the winner. | "I could not find this information in the uploaded documents." | Yes |
| 4. Paraphrased | How is Agentic AI different from ordinary Generative AI? | Explain the difference using the uploaded document. | Relevant chunks about Generative AI and Agentic AI | Answer generated from retrieved context | Yes |
| 5. Irrelevant | What is the capital of France? | Information should not be invented if it is not present. | No relevant document information | "I could not find this information in the uploaded documents." | Yes |

## Evaluation Criteria

### 1. Retrieval

The system should retrieve relevant chunks from the uploaded PDF.

### 2. Grounded Answer

The generated answer should be supported by the retrieved document context.

### 3. Hallucination Prevention

If the required information is not available in the document, the system should not use outside knowledge or invent an answer.

### 4. Source Verification

The application displays:

- Source file
- Page number
- Relevant retrieved content

This allows the generated answer to be verified against the original document.