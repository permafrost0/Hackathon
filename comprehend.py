import json
import boto3
import csv
from io import StringIO

# バケット名, オブジェクト名
BUCKET_NAME = 'バケット名'
OBJECT_KEY_NAME = '取り出すフォルダ'
OUTPUT_OBJECT_KEY_NAME = '出力フォルダ'

# AWS Comprehendクライアントを作成
comprehend = boto3.client('comprehend')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # S3からCSVファイルを取得
    response = s3.get_object(Bucket=BUCKET_NAME, Key=OBJECT_KEY_NAME)
    body = response['Body'].read().decode('utf-8')
    
    # CSVファイルを読み込み、1行ずつ処理
    csv_data = StringIO(body)
    reader = csv.reader(csv_data)
    
    results = []
    for row in reader:
        # 各行をテキストとしてAmazon Comprehendに送る
        text = ' '.join(row)  # CSVの各行を結合して1つのテキストにする
        
        # Sentiment分析
        sentiment_response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
        sentiment_scores = sentiment_response['SentimentScore']
        
        # 結果をCSV形式で準備
        result_row = [
            sentiment_scores['Positive'],
            sentiment_scores['Negative'],
            sentiment_scores['Neutral'],
            sentiment_scores['Mixed']
        ]
        results.append(result_row)
    
    # 出力用のCSVデータを作成
    output_csv = StringIO()
    csv_writer = csv.writer(output_csv)
    csv_writer.writerow(['Positive', 'Negative', 'Neutral', 'Mixed'])  # ヘッダー行の追加
    csv_writer.writerows(results)
    
    # S3に出力CSVファイルを保存
    s3.put_object(Bucket=BUCKET_NAME, Key=OUTPUT_OBJECT_KEY_NAME, Body=output_csv.getvalue())
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'CSV file with sentiment analysis has been successfully generated and saved to S3.'})
    }
