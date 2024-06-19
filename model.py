import boto3
import pandas as pd

# S3クライアントを作成
s3 = boto3.client('s3')

# バケット名とファイル名を指定
bucket_name = 'nes-input-test'
file_name = 'train/train.csv'
local_file_name = 'train.csv'

# ファイルをローカルにダウンロード
s3.download_file(bucket_name, file_name, local_file_name)

# ダウンロードしたファイルをPandas DataFrameに読み込む
df = pd.read_csv(local_file_name)

# データの確認
print(df.head())

# データの前処理
# 例: 欠損値の処理、カテゴリ変数のエンコード、スケーリングなど

# 欠損値を確認
print(df.isnull().sum())

# 欠損値の処理（例: 平均値で補完）
df.fillna(df.mean(), inplace=True)

# カテゴリ変数のエンコード
df = pd.get_dummies(df)

# スケーリング
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaled_df = scaler.fit_transform(df)

# 前処理後のデータ確認
print(pd.DataFrame(scaled_df).head())

# ダウンロードしたファイルをPandas DataFrameに読み込む
df = pd.read_csv(local_file_name)

# データの確認
print(df.head())

# ターゲットカラムの指定
target_column = 'evaluation'  # 例として'target'というカラム名

# 特徴量とターゲットに分割
X = df.drop(target_column, axis=1)
y = df[target_column]

# データの前処理
# 例: 欠損値の処理（ここでは平均値で補完）
X.fillna(X.mean(), inplace=True)

# カテゴリ変数のエンコード
X = pd.get_dummies(X)

# スケーリング
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 訓練データとテストデータに分割
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# モデルのトレーニング
model = RandomForestClassifier()
model.fit(X_train, y_train)

# 予測
y_pred = model.predict(X_test)

# 精度の評価
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy:.2f}')


import boto3

# S3クライアントを作成
s3 = boto3.client('s3')

# バケット名とアップロードするファイルのパスを指定
bucket_name = 'nes-model-test'
s3_model_path = 'random_forest_model.pkl'

# モデルファイルをS3にアップロード
s3.upload_file(model_filename, bucket_name, s3_model_path)