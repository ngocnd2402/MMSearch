import clip
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import skimage.io as io
import PIL.Image
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from tqdm import tqdm, trange
from typing import Tuple, List, Union, Optional
from IPython.display import Image
from clip import load
import os

# Define device constants
CPU = torch.device('cpu')

class DeviceHelper:
    @staticmethod
    def get_device(device_id: int) -> torch.device:
        if not torch.cuda.is_available():
            return CPU
        device_id = min(torch.cuda.device_count() - 1, device_id)
        return torch.device(f'cuda:{device_id}')

class MLP(nn.Module):
    def __init__(self, sizes: Tuple[int, ...], bias=True, act=nn.Tanh):
        super(MLP, self).__init__()
        layers = []
        for i in range(len(sizes) - 1):
            layers.append(nn.Linear(sizes[i], sizes[i + 1], bias=bias))
            if i < len(sizes) - 2:
                layers.append(act())
        self.model = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)

class ClipCaptionModel(nn.Module):
    def __init__(self, prefix_length: int, prefix_size: int = 512):
        super(ClipCaptionModel, self).__init__()
        self.prefix_length = prefix_length
        self.gpt = GPT2LMHeadModel.from_pretrained('gpt2')
        self.gpt_embedding_size = self.gpt.transformer.wte.weight.shape[1]
        if prefix_length > 10:
            self.clip_project = nn.Linear(prefix_size, self.gpt_embedding_size * prefix_length)
        else:
            self.clip_project = MLP((prefix_size, (self.gpt_embedding_size * prefix_length) // 2, self.gpt_embedding_size * prefix_length))

    def forward(self, tokens: torch.Tensor, prefix: torch.Tensor, mask: Optional[torch.Tensor] = None, labels: Optional[torch.Tensor] = None):
        embedding_text = self.gpt.transformer.wte(tokens)
        prefix_projections = self.clip_project(prefix).view(-1, self.prefix_length, self.gpt_embedding_size)
        embedding_cat = torch.cat((prefix_projections, embedding_text), dim=1)
        if labels is not None:
            dummy_token = self.get_dummy_token(tokens.shape[0], tokens.device)
            labels = torch.cat((dummy_token, tokens), dim=1)
        out = self.gpt(inputs_embeds=embedding_cat, labels=labels, attention_mask=mask)
        return out

    def get_dummy_token(self, batch_size: int, device: torch.device) -> torch.Tensor:
        return torch.zeros(batch_size, self.prefix_length, dtype=torch.int64, device=device)

class TextGenerationHelper:
    @staticmethod
    def generate_beam(model, tokenizer, beam_size: int = 5, prompt=None, embed=None, entry_length=67, temperature=1., stop_token: str = '.'):
        # Function implementation here
        model.eval()
        stop_token_index = tokenizer.encode(stop_token)[0]
        tokens = None
        scores = None
        device = next(model.parameters()).device
        seq_lengths = torch.ones(beam_size, device=device)
        is_stopped = torch.zeros(beam_size, device=device, dtype=torch.bool)
        with torch.no_grad():
            if embed is not None:
                generated = embed
            else:
                if tokens is None:
                    tokens = torch.tensor(tokenizer.encode(prompt))
                    tokens = tokens.unsqueeze(0).to(device)
                    generated = model.gpt.transformer.wte(tokens)
            for i in range(entry_length):
                outputs = model.gpt(inputs_embeds=generated)
                logits = outputs.logits
                logits = logits[:, -1, :] / (temperature if temperature > 0 else 1.0)
                logits = logits.softmax(-1).log()
                if scores is None:
                    scores, next_tokens = logits.topk(beam_size, -1)
                    generated = generated.expand(beam_size, *generated.shape[1:])
                    next_tokens, scores = next_tokens.permute(1, 0), scores.squeeze(0)
                    if tokens is None:
                        tokens = next_tokens
                    else:
                        tokens = tokens.expand(beam_size, *tokens.shape[1:])
                        tokens = torch.cat((tokens, next_tokens), dim=1)
                else:
                    logits[is_stopped] = -float(np.inf)
                    logits[is_stopped, 0] = 0
                    scores_sum = scores[:, None] + logits
                    seq_lengths[~is_stopped] += 1
                    scores_sum_average = scores_sum / seq_lengths[:, None]
                    scores_sum_average, next_tokens = scores_sum_average.view(-1).topk(beam_size, -1)
                    next_tokens_source = next_tokens // scores_sum.shape[1]
                    seq_lengths = seq_lengths[next_tokens_source]
                    next_tokens = next_tokens % scores_sum.shape[1]
                    next_tokens = next_tokens.unsqueeze(1)
                    tokens = tokens[next_tokens_source]
                    tokens = torch.cat((tokens, next_tokens), dim=1)
                    generated = generated[next_tokens_source]
                    scores = scores_sum_average * seq_lengths
                    is_stopped = is_stopped[next_tokens_source]
                next_token_embed = model.gpt.transformer.wte(next_tokens.squeeze()).view(generated.shape[0], 1, -1)
                generated = torch.cat((generated, next_token_embed), dim=1)
                is_stopped = is_stopped + next_tokens.eq(stop_token_index).squeeze()
                if is_stopped.all():
                    break
        scores = scores / seq_lengths
        output_list = tokens.cpu().numpy()
        output_texts = [tokenizer.decode(output[:int(length)]) for output, length in zip(output_list, seq_lengths)]
        order = scores.argsort(descending=True)
        output_texts = [output_texts[i] for i in order]
        return output_texts

    @staticmethod
    def generate2(model, tokenizer, tokens=None, prompt=None, embed=None, entry_count=1, entry_length=67, top_p=0.8, temperature=1., stop_token: str = '.'):
        # Function implementation here
        model.eval()
        generated_num = 0
        generated_list = []
        stop_token_index = tokenizer.encode(stop_token)[0]
        filter_value = -float("Inf")
        device = next(model.parameters()).device

        with torch.no_grad():

            for entry_idx in trange(entry_count):
                if embed is not None:
                    generated = embed
                else:
                    if tokens is None:
                        tokens = torch.tensor(tokenizer.encode(prompt))
                        tokens = tokens.unsqueeze(0).to(device)

                    generated = model.gpt.transformer.wte(tokens)

                for i in range(entry_length):

                    outputs = model.gpt(inputs_embeds=generated)
                    logits = outputs.logits
                    logits = logits[:, -1, :] / (temperature if temperature > 0 else 1.0)
                    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                    cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    indices_to_remove = sorted_indices[sorted_indices_to_remove]
                    logits[:, indices_to_remove] = filter_value
                    next_token = torch.argmax(logits, -1).unsqueeze(0)
                    next_token_embed = model.gpt.transformer.wte(next_token)
                    if tokens is None:
                        tokens = next_token
                    else:
                        tokens = torch.cat((tokens, next_token), dim=1)
                    generated = torch.cat((generated, next_token_embed), dim=1)
                    if stop_token_index == next_token.item():
                        break

                output_list = list(tokens.squeeze().cpu().numpy())
                output_text = tokenizer.decode(output_list)
                generated_list.append(output_text)
        return generated_list[0]

# Create an instance of DeviceHelper
device_helper = DeviceHelper()

# Create instances of Model classes
prefix_length = 10
model = ClipCaptionModel(prefix_length)

# Create instances of TextGenerationHelper
text_generation_helper = TextGenerationHelper()

# Load model weights
model_path = 'weights/model_wieghts.pt'
model.load_state_dict(torch.load(model_path, map_location=CPU), strict=False)
model = model.eval()
model = model.to(device_helper.get_device(0))

def generate_caption_for_image(image_path, model, clip_model, tokenizer, prefix_length, use_beam_search=True):
    # Load image
    image = io.imread(image_path)
    pil_image = PIL.Image.fromarray(image)
    image = preprocess(pil_image).unsqueeze(0).to(device)

    # Generate Text
    with torch.no_grad():
        prefix = clip_model.encode_image(image).to(device, dtype=torch.float32)
        prefix_embed = model.clip_project(prefix).reshape(1, prefix_length, -1)
    if use_beam_search:
        generated_text_prefix = text_generation_helper.generate_beam(model, tokenizer, embed=prefix_embed)[0]
    else:
        generated_text_prefix = text_generation_helper.generate2(model, tokenizer, embed=prefix_embed)

    return generated_text_prefix

# Load CLIP model and GPT2 tokenizer
device = device_helper.get_device(0)
print(device)

clip_model, preprocess = load("ViT-B/32", device=device, jit=True)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
use_beam_search = True

from natsort import natsorted
import json
json_file_path = 'CLIPCAP.json'
# Define the root directory containing the keyframes
root_dir = 'AIC2023/Keyframes'

# Create an empty dictionary to store captions and image paths
caption_dict = {}

# Move the model and data to the GPU
model.to(device)
clip_model.to(device)

# Loop through subdirectories at the first level (e.g., L01, L02, ...)
for level1_dir in natsorted(os.listdir(root_dir)):
    level1_path = os.path.join(root_dir, level1_dir)
    
    # Loop through subdirectories at the second level (e.g., L01_V001, L01_V002, ...)
    for level2_dir in natsorted(os.listdir(level1_path)):
        level2_path = os.path.join(level1_path, level2_dir)
        
        # Loop through image files (e.g., 0001.jpg, 0002.jpg, ...)
        for file in natsorted(os.listdir(level2_path)):
            if file.lower().endswith('.jpg'):
                image_path = os.path.join(level2_path, file)
                print("Processing:", image_path)  # Print the current image being processed
                caption = generate_caption_for_image(image_path, model, clip_model, tokenizer, prefix_length, use_beam_search)
                print(f'Frame {image_path} caption: {caption}')
                caption_dict[caption] = image_path
                
                # Update the JSON file incrementally
                with open(json_file_path, 'w') as json_file:
                    json.dump(caption_dict, json_file, indent=4)
                
                print("JSON file updated:", json_file_path)

print("Processing finished!")
