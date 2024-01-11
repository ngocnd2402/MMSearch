import json

# Đường dẫn tới tệp JSON đầu vào và đầu ra
input_file = "/mmlabworkspace/Students/ngocnd/JSON/BLIPCAP.json"
output_file = "/mmlabworkspace/Students/ngocnd/JSON/BLIPCAP_final.json"

# Đọc tệp JSON đầu vào
with open(input_file, "r") as f:
    data = json.load(f)

# Chuyển đổi dữ liệu và chỉ lấy phần "L04/V015.0001"
count = 0

new_data = []

for key, value in data.items():
    
    
    new_data.append({
        "id": count,
        "frame": f"{key.split('/')[-3]}/{key.split('/')[-2].split('_')[1]}/{key.split('/')[-1].split('.')[0]}",
        "caption": value
    })
    
    count += 1

# Ghi mảng JSON mới vào tệp đầu ra
with open(output_file, "w") as f:
    json.dump(new_data, f, indent=4)

print("Chuyển đổi hoàn tất. Kết quả được lưu trong", output_file)
