import json

def create_inverted_index(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    inverted_index = {}
    for image_path, objects in data.items():
        for object_name, bboxes in objects.items():
            if object_name not in inverted_index:
                inverted_index[object_name] = {}
            if image_path not in inverted_index[object_name]:
                inverted_index[object_name][image_path] = []
            inverted_index[object_name][image_path].extend(bboxes)
    return inverted_index

def write_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

input_json_file_path = '/home/visedit/WorkingSpace/AIC2023/JSON/object.json'
output_json_file_path = '/home/visedit/WorkingSpace/AIC2023/JSON/inverted_file.json'
inverted_index = create_inverted_index(input_json_file_path)
write_json(inverted_index, output_json_file_path)
