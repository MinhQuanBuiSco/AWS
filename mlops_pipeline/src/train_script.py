from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import load_dataset
import os
import json
import math

def main():
    model_name = os.environ.get("HF_MODEL_NAME", "facebook/opt-125m")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    dataset = load_dataset('wikitext', 'wikitext-103-raw-v1', split='train[:1%]')
    tokenized = dataset.map(lambda x: tokenizer(x["text"], truncation=True, padding="max_length"), batched=True)

    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    args = TrainingArguments(
        output_dir="/opt/ml/model",
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        num_train_epochs=1,
        weight_decay=0.01,
        logging_dir="/opt/ml/output/logs",
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        tokenizer=tokenizer,
        data_collator=collator
    )

    trainer.train()
    metrics = trainer.evaluate()

    # ➕ Add perplexity to metrics
    if "eval_loss" in metrics:
        metrics["perplexity"] = math.exp(metrics["eval_loss"])

    # Save metrics
    with open("/opt/ml/model/eval_results.json", "w") as f:
        json.dump(metrics, f)
        
if __name__ == "__main__":
    main()
