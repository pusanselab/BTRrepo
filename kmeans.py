from elasticsearch import Elasticsearch
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.cm as cm

# 1. Elasticsearch 연결 설정
es = Elasticsearch("http://localhost:9200")  # Elasticsearch 서버 주소

# 2. Elasticsearch에서 데이터 가져오기
def fetch_data_from_elasticsearch(index_name, size=10000):
    query = {
        "size": size,
        "sort": [{"timestamp": {"order": "asc"}}],  # timestamp 기준 정렬
        "_source": ["timestamp", "from", "to", "function_info"]  # 필요한 필드만 선택
    }
    response = es.search(index=index_name, body=query)
    hits = response['hits']['hits']
    data = [hit["_source"] for hit in hits]  # '_source'에서 데이터 추출
    return pd.DataFrame(data)

# 트랜잭션 데이터 가져오기
index_name = "transactions"
transactions = fetch_data_from_elasticsearch(index_name)

# 3. 데이터 전처리: 실행 시간 계산
transactions['timestamp'] = pd.to_datetime(transactions['timestamp'])  # datetime 변환
transactions.sort_values(by='timestamp', inplace=True)  # 시간순 정렬

# 실행 시간 (ms) 계산
transactions['execution_time'] = transactions['timestamp'].diff().dt.total_seconds() * 1000  # 실행 시간 (ms)

# NaN 제거 (첫 번째 값은 실행 시간이 계산되지 않음)
transactions = transactions.dropna(subset=['execution_time'])

# Order ID는 function_info에서 추출
transactions['order_id'] = transactions['function_info'].apply(
    lambda x: x.get('parameters', {}).get('_orderId') if isinstance(x, dict) and 'parameters' in x else None
)

# NaN 제거 (Order ID 없는 경우 제외)
transactions = transactions.dropna(subset=['order_id'])

# 4. 실행 시간 정규화
scaler = StandardScaler()
execution_times_scaled = scaler.fit_transform(transactions[['execution_time']])

# 5. 군집화 (K-Means)
kmeans = KMeans(n_clusters=2, random_state=42)
transactions['cluster'] = kmeans.fit_predict(execution_times_scaled)

# 6. 이상치 탐지 (Isolation Forest)
iso_forest = IsolationForest(contamination=0.05, random_state=42)
transactions['anomaly'] = iso_forest.fit_predict(execution_times_scaled)

# IsolationForest 스코어 계산
transactions['anomaly_score'] = iso_forest.decision_function(execution_times_scaled)

# 경계값 계산 (IsolationForest 이상치 기준)
threshold = np.percentile(transactions['anomaly_score'], 5)  # 이상치 기준(5% contamination)

# 데이터 정렬 (원본 유지)
transactions.reset_index(drop=True, inplace=True)
transactions['index'] = range(len(transactions))  # X축: 원본 트랜잭션 인덱스

# Order ID별 색상 매핑
unique_order_ids = transactions['order_id'].unique()
cmap = cm.get_cmap("tab20", len(unique_order_ids))
order_id_to_color = {order_id: cmap(i) for i, order_id in enumerate(unique_order_ids)}
transactions['color'] = transactions['order_id'].map(order_id_to_color)

# 시각화
plt.figure(figsize=(14, 7))

# 정상 데이터 표시 (Order ID별 색상)
for order_id in unique_order_ids:
    subset = transactions[(transactions['order_id'] == order_id) & (transactions['anomaly'] == 1)]
    plt.scatter(
        subset['index'],
        subset['execution_time'],
        color=order_id_to_color[order_id],
        label=f"Order {order_id}",
        alpha=0.6
    )

# 경계값 표시 (IsolationForest의 이상치 기준선)
plt.axhline(
    y=scaler.inverse_transform([[threshold]])[0][0],  # 경계값을 원본 실행 시간 값으로 변환
    color="red",
    linestyle="--",
    label="Anomaly Threshold"
)

# 이상치 데이터 표시 (Order ID와 무관, 원본 데이터 유지)
anomalies = transactions[transactions['anomaly'] == -1]
plt.scatter(
    anomalies['index'],
    anomalies['execution_time'],
    color="red",
    label="Anomalous Transactions",
    alpha=0.6,
    s=50
)

# 그래프 설정
plt.xlabel("Transaction Index")
plt.ylabel("Execution Time (ms)")
plt.title("Transaction Execution Time Anomaly Detection")
plt.legend(
    loc="upper left",  # 상단 중앙 위치
    bbox_to_anchor=(1, 1),  # 그래프 아래쪽으로 이동  # 한 줄에 표시할 열 개수
    fontsize=9  # 레전드 글자 크기 조정
)
plt.tight_layout()
plt.grid()
plt.savefig("./exam1.png")
plt.show()
print(scaler.inverse_transform([[threshold]])[0][0])
