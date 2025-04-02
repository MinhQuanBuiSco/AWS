from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline
import json
import numpy as np

def model_fn(model_dir):
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForTokenClassification.from_pretrained(model_dir)
    ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    return ner_pipeline

def input_fn(request_body, request_content_type):
    if request_content_type == "application/json":
        return json.loads(request_body)  # ✅ Convert to dict
    raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    # input_data is expected to be a dict with a 'text' field
    text = input_data.get("text", "")
    return model(text)

def output_fn(prediction, content_type):
    if content_type == "application/json":
        # ✅ Convert any NumPy types (like float32) to Python-native types
        def convert(o):
            if isinstance(o, (np.float32, np.float64)):
                return float(o)
            elif isinstance(o, (np.int32, np.int64)):
                return int(o)
            elif isinstance(o, np.ndarray):
                return o.tolist()
            raise TypeError(f"Object of type {type(o)} is not JSON serializable")

        return json.dumps(prediction, default=convert)
    
    raise ValueError(f"Unsupported content type: {content_type}")