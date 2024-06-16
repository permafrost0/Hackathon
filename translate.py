import json
import boto3
import csv

# 入力バケットと出力バケットの名前
BUCKET_NAME = 'バケット名'
OBJECT_KEY_NAME = '取り出すフォルダ'
OUTPUT_OBJECT_KEY_NAME = '出力フォルダ'

s3 = boto3.client('s3')
translate = boto3.client('translate')

def lambda_handler(event, context):
    # S3から入力ファイルを取得
    response = s3.get_object(Bucket=BUCKET_NAME, Key=OBJECT_KEY_NAME)
    body = response['Body'].read().decode('utf-8')
    
    # テキストを改行で分割して各行を翻訳し、リストに格納
    lines = body.splitlines()
    translated_lines = []
    
    for line in lines:
        # 空行をスキップする
        if line.strip() == '':
            continue
        
        # Amazon Translateを使用して翻訳
        translation_response = translate.translate_text(
            Text=line,  # 各行ごとに翻訳するように修正
            SourceLanguageCode='ja',
            TargetLanguageCode='en'
        )
        translated_text = translation_response['TranslatedText']
        
        # 翻訳されたテキストを一文にまとめる
        one_sentence_text = translated_text.replace('\n', ' ').replace(',', ' ').replace('.', '. ').replace('  ', ' ').strip()
        translated_lines.append(one_sentence_text)
    
    # 一文にまとめたテキストをS3に保存
    translated_text = '\n'.join(translated_lines)
    s3.put_object(Bucket=BUCKET_NAME, Key=OUTPUT_OBJECT_KEY_NAME, Body=translated_text.encode('utf-8'))
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Translation completed and saved to S3 as a single sentence per line.'})
    }
