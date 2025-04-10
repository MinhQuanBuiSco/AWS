from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def model_fn(model_dir):
    model = AutoModelForCausalLM.from_pretrained(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    return {"model": model, "tokenizer": tokenizer}

def predict_fn(data, model_artifacts):
    tokenizer = model_artifacts["tokenizer"]
    model = model_artifacts["model"]

    inputs = tokenizer(data["inputs"], return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=50)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"generated_text": result}

def input_fn(request_body, content_type):
    import json
    return json.loads(request_body)

def output_fn(prediction, content_type):
    import json
    return json.dumps(prediction)
