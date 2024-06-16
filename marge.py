import json
import boto3
import csv
from io import StringIO

# バケット名とオブジェクト名
BUCKET_NAME = 'バケット名'
OBJECT_KEY_NAME = ['取り出すフォルダ1','取り出すフォルダ2',...]
OUTPUT_OBJECT_KEY_NAME = '出力フォルダ'

# AWSクライアントを作成
s3 = boto3.client('s3')

def score_evaluation(score):
    if score == "Excellent":
        return 4
    elif score == "Good job":
        return 3
    elif score == "Good":
        return 2
    elif score == "OK":
        return 1
    else:
        return score  # デフォルトは0としますが、必要に応じて他の値に変更可能

def lambda_handler(event, context):
    merged_rows = []
    
    # 各ファイルから行を取得して結合
    for key in OBJECT_KEY_NAMES:
        # S3からCSVファイルを取得
        response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        body = response['Body'].read().decode('utf-8')
        
        # CSVファイルを読み込み、行をリストに格納
        csv_data = StringIO(body)
        reader = csv.reader(csv_data)
        rows = list(reader)  # CSVの全ての行をリストとして取得
        
        if(key == "input/input_eva.csv"):
            print(len(rows))
            for row in rows:
                row[0] = score_evaluation(row[0])
        
        # 行数が同じであることを確認
        if len(merged_rows) == 0:
            merged_rows = rows
        elif len(merged_rows) != len(rows):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Files do not have the same number of rows.'})
            }
        else:
            # 各ファイルの行を結合する
            for i in range(len(merged_rows)):               
                merged_rows[i] += rows[i]
    
    # 出力用のCSVデータを作成
    output_csv = StringIO()
    csv_writer = csv.writer(output_csv)
    
    # 全ての行を書き込む
    csv_writer.writerows(merged_rows)
    
    # S3に出力CSVファイルを保存
    s3.put_object(Bucket=BUCKET_NAME, Key=OUTPUT_OBJECT_KEY_NAME, Body=output_csv.getvalue())
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'CSV files have been successfully merged and saved to S3.'})
    }