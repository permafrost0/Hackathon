import json
import boto3
import csv
import textstat
from io import StringIO

# バケット名, オブジェクト名
BUCKET_NAME = 'バケット名'
OBJECT_KEY_NAME = '取り出すフォルダ'
OUTPUT_OBJECT_KEY_NAME = '出力フォルダ'

s3 = boto3.client('s3')

def calculate_text_statistics(text):
    """
    テキストの統計情報を計算する関数　
    """
    # 文章の読みやすさ
    flesch_reading_ease = textstat.flesch_reading_ease(text)
    # 文章を理解するのに必要な教育年数 (音節と文の長さ)
    flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
    # 文章を理解するのに必要な教育年数 (文の長さと複雑な単語の割合)
    gunning_fog = textstat.gunning_fog(text)
    # 文章を理解するのに必要な教育年数 (文字数と文の長さ)
    automated_readability_index = textstat.automated_readability_index(text)
    # 文章を理解するのに必要な教育年数 (文字数と文の比率)    
    coleman_liau_index = textstat.coleman_liau_index(text)
    # 文章を理解するのに必要な教育年数 (文の長さと単語の複雑さ)        
    linsear_write_formula = textstat.linsear_write_formula(text)
    # 単語の数
    lexicon_count = textstat.lexicon_count(text, removepunct=True)
    # 文の数
    sentence_count = textstat.sentence_count(text)
    
    return flesch_reading_ease, flesch_kincaid_grade, gunning_fog, automated_readability_index, coleman_liau_index, linsear_write_formula, lexicon_count, sentence_count

def lambda_handler(event, context):
    # S3からCSVファイルを取得
    response = s3.get_object(Bucket=BUCKET_NAME, Key=OBJECT_KEY_NAME)
    body = response['Body'].read().decode('utf-8')
    
    # CSVファイルを読み込み、1行ずつ処理
    csv_data = StringIO(body)
    reader = csv.reader(csv_data)
    
    results = []
    for row in reader:
        # 各行をテキストとして結合
        text = ' '.join(row)
        
        # テキストの統計情報を計算
        flesch_reading_ease, flesch_kincaid_grade, gunning_fog, automated_readability_index, coleman_liau_index, linsear_write_formula, lexicon_count, sentence_count = calculate_text_statistics(text)
        
        # 結果をCSV形式で準備
        result_row = [flesch_reading_ease, flesch_kincaid_grade, gunning_fog, automated_readability_index, coleman_liau_index, linsear_write_formula, lexicon_count, sentence_count]  # 統計情報をそれぞれの列に配置
        results.append(result_row)
    
    # 出力用のCSVデータを作成
    output_csv = StringIO()
    csv_writer = csv.writer(output_csv)
    csv_writer.writerow(["flesch_reading_ease", "flesch_kincaid_grade", "gunning_fog", "automated_readability_index", "coleman_liau_index", "linsear_write_formula", "lexicon_count", "sentence_count"])  # ヘッダー行の追加
    csv_writer.writerows(results)
    
    # S3に出力CSVファイルを保存
    s3.put_object(Bucket=BUCKET_NAME, Key=OUTPUT_OBJECT_KEY_NAME, Body=output_csv.getvalue())
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'CSV file with text statistics has been successfully generated and saved to S3.'})
    }
