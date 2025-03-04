# Slack
SLACK_WORKSPACE_NAME="ragtestspace"


# HuggingFace
HF_EMBEDDING_MODEL_NAME="multi-qa-distilbert-cos-v1"
"""
   Other models to consider:
   nvidia/NV-Embed-v2
   sentence-transformers/all-mpnet-base-v2
   sentence-transformers/all-MiniLM-L6-v2
   qwen has a qa model i believe 
"""

# Weaviate
WEAVIATE_COLLECTION_NAME="slack_threads"
K_RETRIEVALS=3
CERTAINTY_THRESHOLD=0.5