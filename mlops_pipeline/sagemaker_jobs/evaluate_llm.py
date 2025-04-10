import boto3
import tarfile
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
import numpy as np
import argparse

def download_model_from_s3(s3_path, local_dir):
    s3 = boto3.client('s3')
    bucket = s3_path.split('/')[2]
    key = '/'.join(s3_path.split('/')[3:]) + 'model.tar.gz'

    os.makedirs(local_dir, exist_ok=True)
    local_tar_path = os.path.join(local_dir, 'model.tar.gz')
    s3.download_file(bucket, key, local_tar_path)

    with tarfile.open(local_tar_path, 'r:gz') as tar:
        tar.extractall(path=local_dir)

    return os.path.join(local_dir, 'model')

def evaluate_perplexity(s3_model_path, dataset_name='wikitext', dataset_config='wikitext-103-raw-v1'):
    local_model_dir = '/tmp/model'
    model_dir = download_model_from_s3(s3_model_path, local_model_dir)

    model = AutoModelForCausalLM.from_pretrained(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)

    val_dataset = load_dataset(dataset_name, dataset_config, split='validation[:1%]')

    def tokenize_function(examples):
        return tokenizer(examples['text'], padding='max_length', truncation=True, max_length=128)

    tokenized_val = val_dataset.map(tokenize_function, batched=True, remove_columns=['text'])

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    text = '\n'.join(tokenized_val['input_ids'])
    encodings = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    input_ids = encodings.input_ids.to(device)
    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
        loss = outputs.loss
        perplexity = torch.exp(loss)

    print(f"Perplexity: {perplexity.item()}")
    return perplexity.item()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate LLM model')
    parser.add_argument('--bucket-name', type=str, required=True, help='S3 bucket name')
    args = parser.parse_args()
    model_path = f's3://{args.bucket_name}/output/model/'
    perplexity_score = evaluate_perplexity(model_path)
    with open('eval_results.txt', 'w') as f:
        f.write(f"Perplexity: {perplexity_score}")