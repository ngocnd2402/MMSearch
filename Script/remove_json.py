import json

# Đọc tệp JSON ban đầu vào biến data
json_file_path = "JSON/asr_batch2.json"
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# Tính toán điểm chia dữ liệu thành hai phần
split_point = len(data) // 2

# Chia dữ liệu thành hai phần
data_part1 = data[:split_point]
data_part2 = data[split_point:]

# Đặt tên cho hai tệp JSON mới
json_file_path_part1 = "JSON/ocr_batch_3.1.json"
json_file_path_part2 = "JSON/ocr_batch_3.2.json"

# Ghi dữ liệu của hai phần vào hai tệp JSON mới
with open(json_file_path_part1, 'w', encoding='utf-8') as json_file_part1:
    json.dump(data_part1, json_file_part1, ensure_ascii=False, indent=4)

with open(json_file_path_part2, 'w', encoding='utf-8') as json_file_part2:
    json.dump(data_part2, json_file_part2, ensure_ascii=False, indent=4)

print("Dữ liệu đã được chia thành hai tệp JSON: ocr_batch_3.1 và ocr_batch_3.2")
