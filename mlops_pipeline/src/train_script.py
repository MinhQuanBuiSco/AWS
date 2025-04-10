from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.get_logger(__name__)

def main():
    model_name = os.environ.get('SM_HPS_MODEL_NAME_OR_PATH', 'facebook/opt-125m')
    dataset_name = os.environ.get('SM_HPS_DATASET_NAME', 'wikitext')
    dataset_config = os.environ.get('SM_HPS_DATASET_CONFIG_NAME', 'wikitext-103-raw-v1')
    max_seq_length = int(os.environ.get('SM_HPS_MAX_SEQ_LENGTH', 128))
    num_train_epochs = float(os.environ.get('SM_HPS_NUM_TRAIN_EPOCHS', 3))
    per_device_train_batch_size = int(os.environ.get('SM_HPS_PER_DEVICE_TRAIN_BATCH_SIZE', 4))

    logger.info(f"Starting training with model: {model_name}, dataset: {dataset_name}, config: {dataset_config}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    dataset = load_dataset(dataset_name, dataset_config, split='train[:1%]')

    def tokenize_function(examples):
        return tokenizer(examples['text'], padding='max_length', truncation=True, max_length=max_seq_length)

    tokenized_datasets = dataset.map(tokenize_function, batched=True, remove_columns=['text'])

    training_args = TrainingArguments(
        output_dir=os.environ.get('SM_MODEL_DIR', './results'),
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=per_device_train_batch_size,
        save_strategy='epoch',
        logging_dir='./logs',
        logging_steps=10,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets,
    )

    logger.info("Starting training...")
    trainer.train()

    logger.info(f"Saving model to {os.environ.get('SM_MODEL_DIR')}")
    trainer.save_model()
    tokenizer.save_pretrained(os.environ.get('SM_MODEL_DIR'))

if __name__ == '__main__':
    main()