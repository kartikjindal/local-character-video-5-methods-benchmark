#!/bin/zsh
# Downloads every model used by approaches 2 and 3 (~23 GB) in parallel into the Hugging Face cache.
cd "$(dirname "$0")"
H=.venv-ai/bin/hf
$H download SG161222/RealVisXL_V4.0 model_index.json scheduler/scheduler_config.json text_encoder/config.json text_encoder/model.fp16.safetensors text_encoder_2/config.json text_encoder_2/model.fp16.safetensors tokenizer/merges.txt tokenizer/special_tokens_map.json tokenizer/tokenizer_config.json tokenizer/vocab.json tokenizer_2/merges.txt tokenizer_2/special_tokens_map.json tokenizer_2/tokenizer_config.json tokenizer_2/vocab.json unet/config.json unet/diffusion_pytorch_model.fp16.safetensors vae/config.json vae/diffusion_pytorch_model.fp16.safetensors &
$H download madebyollin/sdxl-vae-fp16-fix config.json diffusion_pytorch_model.safetensors &
$H download Lightricks/LTX-Video-0.9.5 model_index.json scheduler/scheduler_config.json transformer/config.json transformer/diffusion_pytorch_model.safetensors vae/config.json vae/diffusion_pytorch_model.safetensors tokenizer/added_tokens.json tokenizer/special_tokens_map.json tokenizer/spiece.model tokenizer/tokenizer_config.json &
$H download city96/t5-v1_1-xxl-encoder-bf16 &
wait
