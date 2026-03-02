import json
from extraction_acc import compute_json_accuracy
import pandas as pd
from typing import Literal
predicted_report={
    'llama_3':[    
    r"reports_llama\invoice-0-4.json",
    r"reports_llama\invoice-1-3.json",
    r"reports_llama\invoice-2-1.json",
    r"reports_llama\invoice-7-0.json",
    r"reports_llama\MAHESH-R-FlowCV-Resume-20251106.json"],
    'gpt':[
    r"reports_gpt\invoice-0-4.json",
    r"reports_gpt\invoice-1-3.json",
    r"reports_gpt\invoice-2-1.json",
    r"reports_gpt\invoice-7-0.json",
    r"reports_gpt\MAHESH-R-FlowCV-Resume-20251106.json"
    ],
    'llama_3.3':[
    r"reports_llama_80\invoice-0-4.json",
    r"reports_llama_80\invoice-1-3.json",
    r"reports_llama_80\invoice-2-1.json",
    r"reports_llama_80\invoice-7-0.json",
    r"reports_llama_80\MAHESH-R-FlowCV-Resume-20251106.json"
    ]
}
ground_truth_report=[
    r"ground_truth\invoice_0-4.json",
    r"ground_truth\invoice_1-3.json",
    r"ground_truth\invoice_2-1.json",
    r"ground_truth\invoice_7-0.json",
    r"ground_truth\mahesh_resume.json"
]


def json_con(file_path):
     with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data
def test_df_generator(model_name:Literal['gpt','llama_3','llama_3.3']):
    test_dict={
    'model_name':[],
    'file_name':[],
    # 'ground_truth':[],
    # 'predicted_json':[],
    'Extraction_accuracy':[],
    'PII_precision':[],
    'PII_recall':[],
    'PII_F1':[]
    }
    predicted_report_path=predicted_report.get(model_name,[])
    if not predicted_report_path:
        return 'Give valid model_name'
    for pred,ground in zip(predicted_report_path,ground_truth_report):
        gt_data=json_con(ground)
        pr_report=json_con(pred)
        pii_metrics=pr_report.get("redaction",{}).get("pii_metrics")
        precision=pii_metrics["precision"]
        recall=pii_metrics["recall"]
        f1=pii_metrics["f1"]
        pr_data=pr_report.get("extracted_json")
        accuracy,*others=compute_json_accuracy(gt_data,pr_data)
        #test_dict["predicted_json"].append(pr_data)
        test_dict['model_name'].append(model_name)
        test_dict['file_name'].append(pr_report['file_name'])
        #test_dict['ground_truth'].append(gt_data)
        test_dict['Extraction_accuracy'].append(accuracy)
        test_dict['PII_precision'].append(precision*100)
        test_dict['PII_recall'].append(recall*100)
        test_dict['PII_F1'].append(f1*100)
    #print(test_dict)
    test_report=pd.DataFrame(test_dict)
    # print(test_report)
    print(test_report.describe().iloc[1,:])
    # test_report.to_csv('test_report_final.csv')
    return test_report
test_final_report=pd.DataFrame()
for model_name in ['gpt','llama_3','llama_3.3']:
    df=test_df_generator(model_name)
    test_final_report=pd.concat([test_final_report,df],ignore_index=True)
test_final_report.to_csv('test_final_report.csv',index=False)



