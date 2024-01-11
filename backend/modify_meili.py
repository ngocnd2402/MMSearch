from meili import Meilisearch

ocr_index = Meilisearch('OCR')
print(ocr_index.check_health_status())
ocr_index.delete()
print(ocr_index.check_health_status())
ocr_index.insert('JSON/ocr_Batch1.json')
ocr_index.insert('JSON/ocr_Batch2.json')
ocr_index.insert('JSON/ocr_Batch3.json')
print(ocr_index.check_health_status())

asr_index = Meilisearch('ASR')
asr_index.delete()
asr_index.insert('JSON/asr_Batch1.json')
asr_index.insert('JSON/asr_Batch2.json')
asr_index.insert('JSON/asr_Batch3.json')
print(asr_index.check_health_status())