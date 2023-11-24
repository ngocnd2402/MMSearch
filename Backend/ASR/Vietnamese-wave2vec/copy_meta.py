import shutil
import os

source_folder = '/mmlabworkspace/Students/ngoc_AIC2023/Frontend/Mapping'
destination_folder = '/mmlabworkspace/Students/ngoc_AIC2023/Backend/ASR/tests'


# Lặp qua tất cả các tệp trong thư mục nguồn
for root, dirs, files in os.walk(source_folder):

    for file in sorted(files):
        
        if file.endswith('.csv'):
                if 11 <= (folder_number := int(file.split('.')[0][1:3])) <= 20:
                    source_file = os.path.join(root, file)
                    destination_file = os.path.join(destination_folder, file)
                    shutil.copy(source_file, destination_file)
                    print(f'Copied {source_file} to {destination_file}')
                
                print(folder_number)

print('Copy completed.')
