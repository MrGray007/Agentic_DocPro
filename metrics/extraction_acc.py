# from extraction_acc import get_extraction_acc
# from extractor_acc_not_strict import get_extraction_acc
# from extractor_acc_deep import get_extraction_acc
# import json
import json
from deepdiff import DeepDiff

def normalize_json(data):
    """
    Recursively convert numeric strings to numbers for fair comparison.
    """
    if isinstance(data, dict):
        return {k: normalize_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_json(x) for x in data]
    elif isinstance(data, str):
        # Try converting to int or float
        try:
            if '.' in data:
                return float(data)
            else:
                return int(data)
        except ValueError:
            return data
    else:
        return data

def compute_json_accuracy(ground_json, predicted_json):
    """
    Compare two JSONs and return a match accuracy (0-100%)
    """
    # Use DeepDiff to find differences
    ground_json=normalize_json(ground_json)
    predicted_json=normalize_json(predicted_json)
    diff = DeepDiff(ground_json, predicted_json, ignore_order=True)
    
    # Count total comparable items in ground truth
    def count_items(d):
        if isinstance(d, dict):
            return sum(count_items(v) for v in d.values())
        elif isinstance(d, list):
            return sum(count_items(v) for v in d)
        else:
            return 1
    
    total_items = count_items(ground_json)
    
    # Count differences from DeepDiff
    diff_count = 0
    for key in ['values_changed', 'dictionary_item_added', 'dictionary_item_removed',
                'iterable_item_added', 'iterable_item_removed', 'type_changes']:
        diff_count += len(diff.get(key, {}))
    
    accuracy = max((total_items - diff_count) / total_items * 100, 0)
    
    return accuracy,total_items, diff_count,diff
def get_accuracy(gt_file,pd_file):
    with open(gt_file, 'r', encoding='utf-8') as f:
        gt_data = json.load(f)

    with open(pd_file, 'r', encoding='utf-8') as f:
        pred_data = json.load(f)
    pred_data=pred_data.get("extracted_json")
    pred_data.pop("confidence")
    accuracy,total_items, diff_count,diff=compute_json_accuracy(gt_data, pred_data)
    print(f"Extraction Accuracy: {accuracy:.4f}")
    # print(f"Correct Fields: {correct} / {total}")
    #print(f"Incorrect / Missing Fields: {diff}")

    return accuracy
    

# predicted_report=[
#     r"reports\invoice-0-4.json",
#     r"reports\invoice-1-3.json",
#     r"reports\invoice-2-1.json",
#     r"reports\invoice-7-0.json",
#     r"reports\MAHESH-R-FlowCV-Resume-20251106.json"
# ]
# ground_truth_report=[
#     r"ground_truth\invoice_0-4.json",
#     r"ground_truth\invoice_1-3.json",
#     r"ground_truth\invoice_2-1.json",
#     r"ground_truth\invoice_7-0.json",
#     r"ground_truth\mahesh_resume.json"
# ]
# acc=[]
# for pred,ground in zip(predicted_report,ground_truth_report):
#     print(pred.split('\\')[-1])
#     acc.append(get_accuracy(ground,pred))
# print(sum(acc)/len(acc))
# # print(json.loads("ground_truth\invoice-0-4.json"))
