from meilisearch_class import Meilisearch

ocr_index = Meilisearch('OCR')
print(ocr_index.check_health_status())
# ocr_index.delete()
print(ocr_index.check_health_status())
ocr_index.insert('JSON/ocr_batch_31.json')
ocr_index.insert('JSON/ocr_batch_32.json')
# ocr_index.insert('JSON/ocr_batch2.json')
print(ocr_index.check_health_status())

# asr_index = Meilisearch('ASR')
# asr_index.delete()
# asr_index.insert('JSON/asr_batch1.json')
# asr_index.insert('JSON/asr_batch2.json')
# print(asr_index.check_health_status())