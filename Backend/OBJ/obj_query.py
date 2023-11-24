import json
import concurrent.futures

class ObjectRetrieval:
    
    def __init__(self, json_file_path: str):
        with open(json_file_path, 'r') as file:
            self.data = json.load(file)

    @staticmethod
    def calculate_iou(box1, box2):
        """
        Calculate the Intersection over Union (IoU) of two bounding boxes.
        """
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[0] + box1[2], box2[0] + box2[2])
        y2 = min(box1[1] + box1[3], box2[1] + box2[3])

        intersection_area = max(0, x2 - x1) * max(0, y2 - y1)
        box1_area = box1[2] * box1[3]
        box2_area = box2[2] * box2[3]

        if box1_area + box2_area - intersection_area == 0:
            return 0
        iou = intersection_area / float(box1_area + box2_area - intersection_area)
        return iou

    def process_bbox(self, query):
        """
        Process a single bbox.
        """
        results = {}
        query_box = [query['x'], query['y'], query['w'], query['h']]
        query_label = query['label']

        if query_label in self.data:
            for frame, bboxes in self.data[query_label].items():
                max_iou_for_frame = 0
                for bbox in bboxes:
                    iou = self.calculate_iou(query_box, bbox)
                    max_iou_for_frame = max(max_iou_for_frame, iou)
                if max_iou_for_frame > 0:
                    if frame not in results:
                        results[frame] = {}
                    results[frame][query_label] = max_iou_for_frame
        return results

    def search_image(self, query_input, topk=10):
        results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_bbox, query) for query in query_input]
            for future in concurrent.futures.as_completed(futures):
                bbox_results = future.result()
                for frame, label_iou in bbox_results.items():
                    if frame not in results:
                        results[frame] = label_iou
                    else:
                        results[frame].update(label_iou)

        all_labels = {query['label'] for query in query_input}
        filtered_results = {frame: ious for frame, ious in results.items() if all_labels.issubset(ious)}
        final_scores = {frame: sum(ious.values()) for frame, ious in filtered_results.items()}
        sorted_results = [{'frame': frame, 'IOU': iou} for frame, iou in sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:topk]]
        return sorted_results

    
# # Example Usage
# retrieval = ObjectRetrieval('JSON/inverted_file.json')
# query_input = [
#     {'x': 0.7295, 'y': 0.4383, 'w': 0.0114, 'h': 0.0505, 'label': 'traffic light'},
#     {'x': 0.7295, 'y': 0.4383, 'w': 0.0114, 'h': 0.0505, 'label': 'dog'},
#     {'x': 0.7295, 'y': 0.4383, 'w': 0.0114, 'h': 0.0505, 'label': 'traffic light'}
# ]
# topk = 5  
# results = retrieval.search_image(query_input, topk)
# for result in results:
#     print(result)