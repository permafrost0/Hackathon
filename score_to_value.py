import json
import boto3
import csv
from io import BytesIO
import pandas as pd

# バケット名とオブジェクト名
BUCKET_NAME = 'nes-input-test'
OBJECT_KEY_NAMES = "input/input_eva.csv"
OUTPUT_OBJECT_KEY_NAME = 'score/score.csv'

# S3クライアントの作成
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # S3からCSVファイルの読み込み
    response = s3.get_object(Bucket=BUCKET_NAME, Key=OBJECT_KEY_NAMES)
    df = pd.read_csv(response['Body'])

    # 評価を数値に変換するマッピング
    evaluation_mapping = {
        'Excellent': 4,
        'Good job': 3,
        'Good': 2,
        'OK': 1
    }

    # 評価列の変換
    df['score'] = df['evaluation'].map(evaluation_mapping)
    df.drop(columns=['evaluation'], inplace=True)

    # 変換したデータを元のCSVファイルに上書き保存する
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    
    # バッファの位置を先頭に戻す
    csv_buffer.seek(0)

    # S3に上書き保存する
    s3.put_object(Bucket=BUCKET_NAME, Key=OUTPUT_OBJECT_KEY_NAME, Body=csv_buffer)

    return {
        'statusCode': 200,
        'body': 'CSV file converted and saved to S3'
    }
