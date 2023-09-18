python -m vllm.entrypoints.openai.api_server \
    --model eugenepentland/axolotlLLM \
    --tokenizer hf-internal-testing/llama-tokenizer \
    --served-model-name llm \
    --port 8001
