# 📚 Ask My Documents – RAG Assistant

A simple Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask questions based only on the information contained in those documents.

## 🎯 Problem Statement

Large Language Models may generate incorrect or unsupported information when they do not have access to the required source material.

This project uses Retrieval-Augmented Generation to retrieve relevant information from uploaded PDF documents and provide grounded answers with source references.

## 🏗️ Architecture

```text
PDF Upload
    ↓
Document Loading
    ↓
Text Extraction
    ↓
Text Splitting
    ↓
Embedding Generation
    ↓
FAISS Vector Database
    ↓
User Question
    ↓
Similarity Search
    ↓
Top-4 Relevant Chunks
    ↓
LLM with Retrieved Context
    ↓
Grounded Answer
    ↓
Answer + Sources