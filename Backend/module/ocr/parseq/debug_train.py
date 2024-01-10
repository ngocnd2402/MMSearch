from pathlib import PurePath
from typing import Sequence

import torch
from torch import nn

import yaml

# url = 'https://github.com/baudm/parseq/releases/download/v1.0.0/parseq-bb5792a6.pt'
# pretrained_dict = torch.hub.load_state_dict_from_url(url=url, map_location='cpu', check_hash=True)
# for k, v in pretrained_dict.items():
#     print(k)

charset = "AÁÀẠẢÃĂẮẰẲẶẴÂẤẦẨẪẬBCDĐEÈÉẼẺẸÊẾỀỂỄỆFGHIÍÌỈĨỊJKLMNOÒÓỎÕỌÔỐỒỔỖỘƠỚỜỠỞỢPQRSTUÙÚỦŨỤƯỪỨỬỮỰVXYỴÝỲỶỸWZaáàạảãăằắẳẵặâấầẩẫậbcdđeèéẻẽẹêếềểễệfghiíìỉĩịjklmnoòóỏõọôốồổỗộơớờởỡợpqrstuùúủũụưừứửữựvyỳýỷỹỵxwz0123456789'\".,()-%@!/:+?&\\[]=*#<>"
updated_charset = charset + "{}$"
char_count = dict() # pair(char, count)
existing_chars = []

count = 0
with open('./data/train_gt_file.txt') as f:
    rows = f.readlines()
    for row in rows:
        text = row.split()[1]
        for char in text:
            if char not in existing_chars:
                char_count[char] = 0
                existing_chars.append(char)
            char_count[char] += 1

total_chars = set([k for k, v in char_count.items()])
using_chars = set(charset)
missing_chars = total_chars.difference(using_chars)

with open('./data/data_evalutating.txt', 'w') as f:
    f.write(f'--- Using chars: {len(using_chars)}---\n')
    for char in list(total_chars.intersection(using_chars)):
        f.write(f'{char} {char_count[char]}\n')
    f.write(f'--- Missing chars {len(missing_chars)} ---\n')
    for char in list(missing_chars):
        f.write(f'{char} {char_count[char]}\n')

print("{}")