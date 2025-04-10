from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from ts.torch_handler.base_handler import BaseHandler

class Handler(BaseHandler):
    def initialize(self, context):
        self.model = AutoModelForCausalLM.from_pretrained('facebook/opt-125m')
        self.tokenizer = AutoTokenizer.from_pretrained('facebook/opt-125m')
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

    def preprocess(self, data):
        text = data[0]['data']
        inputs = self.tokenizer(text, return_tensors='pt').to(self.device)
        return inputs

    def inference(self, inputs):
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_length=50)
        return [self.tokenizer.decode(output, skip_special_tokens=True) for output in outputs]

    def postprocess(self, inference_output):
        return inference_output