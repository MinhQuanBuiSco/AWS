# sagemaker_scripts/train.py
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from datasets import load_dataset

model_id = "facebook/opt-125m"
dataset = load_dataset("wikitext", "wikitext-2-raw-v1")

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

def tokenize(example):
    return tokenizer(example["text"], padding="max_length", truncation=True, max_length=128)

tokenized_dataset = dataset["train"].map(tokenize, batched=True)

args = TrainingArguments(
    output_dir="/opt/ml/model",
    num_train_epochs=1,
    per_device_train_batch_size=2,
    save_strategy="epoch"
)

trainer = Trainer(model=model, args=args, train_dataset=tokenized_dataset)
trainer.train()