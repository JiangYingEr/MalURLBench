import argparse
import json
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model
import torch

# Argument parser
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_name_or_path",
        type=str,
        required=True,
        help="Base model path (e.g. LLaMA-2-7b-chat-hf)",
    )
    parser.add_argument(
        "--train_file",
        type=str,
        required=True,
        help="Path to training jsonl file",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        required=True,
        help="Output directory for LoRA checkpoints",
    )
    parser.add_argument("--num_train_epochs", type=int, default=1)
    parser.add_argument("--per_device_train_batch_size", type=int, default=1)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=16)
    parser.add_argument("--learning_rate", type=float, default=2e-4)
    parser.add_argument("--max_seq_length", type=int, default=256)
    return parser.parse_args()


# Main
def main():
    args = parse_args()

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name_or_path,
        use_fast=False,
        trust_remote_code=True,
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load dataset
    dataset = load_dataset(
        "json",
        data_files={"train": args.train_file},
    )["train"]

    # Preprocess
    def preprocess(batch):
        conversations = batch["messages"]

        texts = [
            tokenizer.apply_chat_template(
                conv,
                tokenize=False,
                add_generation_prompt=False,
            )
            for conv in conversations
        ]

        enc = tokenizer(
            texts,
            truncation=True,
            max_length=args.max_seq_length,
            padding="max_length",
        )

        # labels = input_ids, but mask padding
        labels = []
        for input_ids, attn_mask in zip(enc["input_ids"], enc["attention_mask"]):
            lbl = input_ids.copy()
            for i in range(len(lbl)):
                if attn_mask[i] == 0:
                    lbl[i] = -100
            labels.append(lbl)

        enc["labels"] = labels
        return enc

    dataset = dataset.map(
        preprocess,
        batched=True,
        remove_columns=dataset.column_names,
    )

    # Load model (QLoRA)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name_or_path,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )

    model.config.use_cache = False

    # LoRA config
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Training args
    training_args = TrainingArguments(
        output_dir=args.out_dir,
        num_train_epochs=args.num_train_epochs,
        per_device_train_batch_size=args.per_device_train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        logging_steps=10,
        save_steps=50,
        save_total_limit=3,
        fp16=False,
        bf16=True,
        report_to="none",
        optim="paged_adamw_8bit",
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )

    trainer.train()
    trainer.save_model(args.out_dir)


if __name__ == "__main__":
    main()
