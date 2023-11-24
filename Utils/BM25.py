from rank_bm25 import BM25Okapi
import string
import json

class BlipSearchEngine:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.load_data()
        self.create_bm25_index()

    def load_data(self):
        with open(self.json_file_path, 'r') as json_file:
            self.data = json.load(json_file)
        self.caption_frame_pairs = [(item['caption'], item['frame']) for item in self.data]

    def create_bm25_index(self):
        punctuations_to_remove = string.punctuation
        cleaned_captions = [self.remove_puncts(caption, punctuations_to_remove) for caption, _ in self.caption_frame_pairs]
        tokenized_captions = [caption.split() for caption in cleaned_captions]
        self.bm25 = BM25Okapi(tokenized_captions)

    def remove_puncts(self, input_string, puncts_to_remove):
        return input_string.translate(str.maketrans('', '', puncts_to_remove)).lower()

    def search(self, query, top_n=100):
        tokenized_query = query.split()

        doc_scores = self.bm25.get_scores(tokenized_query)
        top_doc_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:top_n]

        output_results = [{"frame": self.caption_frame_pairs[index][1]} for index in top_doc_indices]

        return output_results

# Đường dẫn đến file JSON
json_file_path = 'JSON/BLIPCAP_final.json'

# Query riêng
query = "an overturned truck"
blip_search_engine = BlipSearchEngine(json_file_path)
output_results = blip_search_engine.search(query)

print(json.dumps(output_results, indent=2))
