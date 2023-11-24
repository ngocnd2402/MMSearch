import json 
json_path = "/mmlabworkspace/Students/visedit/AIC2023/JSON/asr_Batch2.json"
json_out = "/mmlabworkspace/Students/visedit/AIC2023/JSON/asr_batch2.json"
start_id = 41922

with open(json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

for sample in data:
    sample['id'] = start_id 
    start_id +=1 

with open(json_out, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)
    



    
