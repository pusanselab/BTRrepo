import pandas as pd
import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch
from matplotlib.lines import Line2D

# Elasticsearch 클라이언트 설정
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

# 이더리움 트랜잭션의 함수 이름에 따른 매핑 정보
ETHEREUM_MAPPING = {
    "placeOrder": ("OrderUser", "Seller"),
    "requestManufacture": ("Seller", "Manufacturer"),
    "completeManufacture": {"Manufacturer","Seller"},
    "requestDelivery": ("Seller", "DeliveryAgency"),
    "completeDelivery": {"DeliveryAgency","Seller"},
}

# 노드 매핑 정보
NODE_MAPPING = {
    "OrderUserLocation": "OrderUser",
    "SellerLocation": "Seller",
    "ManufacturerLocation": "Manufacturer",
    "DeliveryAgencyLocation": "DeliveryAgency",
    # 필요에 따라 추가 노드 매핑 설정
}

# Elasticsearch에서 데이터 조회
def fetch_data(index, query, size=1000):
    response = es.search(index=index, body=query, size=size)
    return response['hits']['hits']

# 트랜잭션 데이터 정리
def process_transactions(transactions):
    print(transactions)
    data = []
    for tx in transactions:
        doc = tx["_source"]
        function_info = doc.get("function_info", {})
        function_name = function_info.get("function_name", "N/A")
        parameters = function_info.get("parameters", {})
        mapped_from, mapped_to = ETHEREUM_MAPPING.get(function_name, ("Unknown", "Unknown"))
        # 예상하지 못한 함수 이름이 있을 경우 기본값 설정
        if mapped_from == "Unknown" or mapped_to == "Unknown":
            print(f"Warning: Unexpected function name {function_name} encountered. Using default mapping.")
        filtered_parameters = {k: v for k, v in parameters.items() if k != "_seller"}
        data.append({
            "Function Name": function_name,
            "From": mapped_from,
            "To": mapped_to,
            "Order ID": parameters.get("_orderId", "N/A"),
            "Timestamp": doc.get("timestamp", "N/A"),
            "Details": ", ".join([f"{k}: {v}" for k, v in filtered_parameters.items()]),
        })
    return pd.DataFrame(data)

# Fabric 데이터 정리 (기본 데이터 + Elasticsearch 데이터)
def process_fabric_data(fabric_data, elastic_data):
    legend_data = {}  # 레전드를 위한 데이터 수집
    data = []
    
    # 기존의 기본 데이터 처리
    for doc in fabric_data:
        pattern = doc["_source"].get("pattern", {})
        mapped_node = NODE_MAPPING.get(pattern.get("request_loc"), pattern.get("request_loc"))
        name = pattern.get("name", "N/A")
        address = pattern.get("address", "N/A")
        data.append({
            "Mapped Node": mapped_node,
            "Name": name,
            "Address": address,
            "Phone": pattern.get("phone", "N/A"),
            "Email": pattern.get("email", "N/A"),
        })
        if mapped_node not in legend_data:
            legend_data[mapped_node] = f"{name}, {address}"  # 레전드 항목 생성

    # Elasticsearch에서 가져온 데이터 처리
    for doc in elastic_data:
        pattern = doc["_source"].get("pattern", {})
        mapped_node = NODE_MAPPING.get(pattern.get("request_loc"), pattern.get("request_loc"))
        name = pattern.get("name", "N/A")
        address = pattern.get("address", "N/A")
        data.append({
            "Mapped Node": mapped_node,
            "Name": name,
            "Address": address,
            "Phone": pattern.get("phone", "N/A"),
            "Email": pattern.get("email", "N/A"),
        })
        if mapped_node not in legend_data:
            legend_data[mapped_node] = f"{name}, {address}"  # 레전드 항목 생성
    
    return pd.DataFrame(data), legend_data

# 트랜잭션 및 Fabric 데이터 시각화
def visualize_details(transaction_df, fabric_df, legend_data):
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))  # figsize 조정

    # 트랜잭션 데이터 테이블
    axes[0].axis('off')  # 플롯 축 제거
    table_1 = axes[0].table(cellText=transaction_df.values,
                            colLabels=transaction_df.columns,
                            loc='center',
                            cellLoc='center')
    table_1.auto_set_font_size(False)
    table_1.set_fontsize(10)
    table_1.auto_set_column_width(col=list(range(len(transaction_df.columns))))
    axes[0].set_title("Ethereum Transactions", fontsize=14, pad=10)  # 제목과 테이블 간 간격 줄이기

    # Fabric 데이터 테이블
    axes[1].axis('off')  # 플롯 축 제거
    table_2 = axes[1].table(cellText=fabric_df.values,
                            colLabels=fabric_df.columns,
                            loc='center',
                            cellLoc='center')
    table_2.auto_set_font_size(False)
    table_2.set_fontsize(10)
    table_2.auto_set_column_width(col=list(range(len(fabric_df.columns))))
    axes[1].set_title("Hyperledger Fabric Data", fontsize=14, pad=10)  # 제목과 테이블 간 간격 줄이기

    plt.tight_layout(pad=3.0)  # 레이아웃 간격 더 좁게 설정
    plt.savefig("./test2.png")
    plt.show()

# 실행
order_id = '1'

# 기본 하이퍼레저 패브릭 데이터 (기존에 제공된 데이터)
fabric_data = [
    {
        "_source": {
            "pattern": {
                "request_loc": "Org2MSP",
                "email": "john@example.com",
                "name": "John",
                "order_id": "1",
                "phone": "555-1234",
            }
        }
    },
    {
        "_source": {
            "pattern": {
                "request_loc": "Org3MSP",
                "address": "123 Main St",
                "name": "John",
                "order_id": "1",
                "phone": "555-1234",
            }
        }
    }
]

# Elasticsearch에서 이더리움 트랜잭션 데이터 가져오기
transaction_query = {"query": {"match": {"function_info.parameters._orderId": order_id}}}
transactions = fetch_data(index="transactions", query=transaction_query)

# Elasticsearch에서 하이퍼레저 패브릭 데이터 가져오기
fabric_query = {"query": {"match": {"pattern.order_id": order_id}}}
elastic_fabric_data = fetch_data(index="hyperledgerfabric", query=fabric_query)

# 데이터 처리
transaction_df = process_transactions(transactions)
fabric_df, legend_data = process_fabric_data(fabric_data, elastic_fabric_data)

# 시각화
visualize_details(transaction_df, fabric_df, legend_data)
