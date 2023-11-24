import os
import json
import torch
from transformers import AutoProcessor, Blip2ForConditionalGeneration
from PIL import Image
from natsort import natsorted

# Load the GPT2 tokenizer
tokenizer = AutoProcessor.from_pretrained('Salesforce/blip2-flan-t5-xl')

# Define the root directory containing the keyframes
root_dir = 'Frontend/Keyframe'

# Create an empty dictionary to store captions and image paths
caption_dict = {}

# Load the BLIP2 model
blip2_model = Blip2ForConditionalGeneration.from_pretrained('Salesforce/blip2-flan-t5-xl')

# Move the model to the GPU if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
blip2_model.to(device)

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
                
                # Load image
                pil_image = Image.open(image_path)
                
                # Generate text using BLIP2
                blip_prompt = "Please describe this image exactly as people interpret this photo."
                blip_inputs = tokenizer(pil_image, text=blip_prompt, return_tensors="pt").to(device, torch.float32)  # Use float32
                generated_ids = blip2_model.generate(**blip_inputs, max_length=50)
                generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
                
                print("Generated caption:", generated_text)
                caption_dict[image_path] = generated_text
                
                # Update the JSON file incrementally
                json_file_path = 'BLIP.json'
                with open(json_file_path, 'w') as json_file:
                    json.dump(caption_dict, json_file, indent=4)
                
                print("JSON file updated:", json_file_path)

print("Processing finished!")
