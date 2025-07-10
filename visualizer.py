import networkx as nx
import matplotlib.pyplot as plt
import random
from elasticsearch import Elasticsearch
from matplotlib.lines import Line2D

# Elasticsearch 클라이언트 설정
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

# Elasticsearch에서 데이터 조회 (orderId를 파라미터로 입력받아 해당하는 트랜잭션만 가져오기)
def fetch_transactions(order_id, index="transactions"):
    query = {
        "query": {
            "match": {
                "function_info.parameters._orderId": order_id
            }
        }
    }
    response = es.search(index=index, body=query, size=1000)  # 최대 1000개의 도큐먼트 조회
    return response['hits']['hits']

# Elasticsearch에서 Hyperledger Fabric 데이터 조회 (orderID 기반으로 관련 데이터 가져오기)
def fetch_fabric_data(order_id, index="hyperledgerfabric"):
    query = {
        "query": {
            "match": {
                "pattern.order_id": order_id
            }
        }
    }
    response = es.search(index=index, body=query, size=1000)
    return response['hits']['hits']

# 네트워크 그래프 생성
def create_network_graph(transactions):
    G = nx.DiGraph()  # 방향성 있는 그래프 (화살표로 엣지를 표시하기 위해)

    # 거래 흐름에 따라 'from'과 'to'를 설정할 매핑
    node_mapping = {
        'placeOrder': [('OrderUser', 'Seller')],
        'requestManufacture': [('Seller', 'Manufacturer')],
        'completeManufacture': [('Manufacturer', 'Seller')],
        'requestDelivery': [('Seller', 'DeliveryAgency')],
        'completeDelivery': [('DeliveryAgency', 'Seller')]
    }

    # orderId 기준으로 묶기
    order_dict = {}

    # 노드에 대한 레전드 항목 생성
    legend_labels = {}

    # 엣지 레이블을 위한 딕셔너리
    edge_labels = {}

    for transaction in transactions:
        doc = transaction['_source']
        functioninfo = doc['function_info']
        order_id = functioninfo['parameters'].get('_orderId')
        function_name = functioninfo.get('function_name')
        from_node = doc.get('from')
        to_node = doc.get('to')

        if order_id not in order_dict:
            order_dict[order_id] = []

        if function_name in node_mapping:
            for mapped_from, mapped_to in node_mapping[function_name]:
                order_dict[order_id].append((mapped_from, mapped_to, from_node, to_node, functioninfo['parameters']))

                # 레전드 항목 추가 (mapped_from : from_node, mapped_to : to_node)
                if mapped_from not in legend_labels:
                    legend_labels[mapped_from] = from_node
                if mapped_to not in legend_labels:
                    legend_labels[mapped_to] = to_node

                # 엣지 레이블 추가
                if function_name == list(node_mapping.keys())[0]:
                    edge_label = "\n".join([f"{key}: {value}" for key, value in functioninfo['parameters'].items()])
                    edge_labels[(mapped_from, mapped_to)] = edge_label

    # 네트워크 그래프에 데이터 추가
    for order_id, edges in order_dict.items():
        for mapped_from, mapped_to, from_node, to_node, params in edges:
            G.add_node(mapped_from)
            G.add_node(mapped_to)
            G.add_edge(mapped_from, mapped_to)  # 엣지 추가

    return G, order_dict, legend_labels, edge_labels

# 각 노드별로 고정된 request_loc 매핑 설정
request_loc_mapping = {
    'OrderUser': 'Org1MSP',
    'Seller': 'Org2MSP',
    'DeliveryAgency': 'Org3MSP'
}

# 네트워크 그래프 시각화
def visualize_graph(G, order_dict, legend_labels, edge_labels, fabric_data):
    pos = {}  # 노드 위치 설정

    # 1열에 OrderUser, Seller 배치
    pos['OrderUser'] = (0, 0)
    pos['Seller'] = (1, 0)
    pos['Manufacturer'] = (0, 1)
    pos['DeliveryAgency'] = (1, 1)

    for i, node in enumerate(G.nodes()):
        if node not in pos:
            pos[node] = (i % 2, i // 2 + 1)

    # 그래프 시각화
    plt.figure(figsize=(10, 10))
    connectionstyle = "arc3,rad=0.1"

    nx.draw(G, pos, with_labels=True, node_size=3000, node_color='skyblue', font_size=12, font_weight='bold',
            edge_color='gray', width=2, arrows=True, connectionstyle=connectionstyle)

    # # 엣지 레이블을 엣지의 시작점 (from_node)에 위치시키기 위해 수동으로 배치
    # for (from_node, to_node), label in edge_labels.items():
    #     x1, y1 = pos[from_node]
    #     x2, y2 = pos[to_node]

    #     # 엣지의 중간 위치가 아니라 from_node 근처에 배치
    #     label_x = x1 + 0.1  # x1에 약간 오프셋을 줘서 레이블을 옆으로 배치
    #     label_y = y1 + 0.01  # y1에 약간 오프셋을 줘서 레이블을 옆으로 배치

    #     # 텍스트를 추가
    #     plt.text(label_x, label_y, label, fontsize=8, ha='left', va='bottom', color='blue')

    # # 각 노드에 직사각형 추가 (fabric_data와 매핑 테이블을 기반으로)
    # for node in G.nodes():
    #     # 매핑 테이블에서 해당 노드에 매핑된 request_loc 값 가져오기
    #     mapped_loc = request_loc_mapping.get(node)

    #     # fabric_data에서 매핑된 request_loc 값을 가진 데이터 찾기
    #     for doc in fabric_data:
    #         source_data = doc['_source']
    #         request_loc = source_data['pattern'].get('request_loc')

    #         if request_loc == mapped_loc:  # 매핑된 값과 일치할 때만 표시
    #             x, y = pos[node]
    #             y -= 0.1
    #             rect_width = 0.5
    #             rect_height = 0.2

    #             # 선택된 키만 가져오고, None 값을 제외
    #             fields_to_display = ['request_loc', 'name', 'address', 'phone', 'email']
    #             filtered_data = {key: value for key, value in source_data['pattern'].items() 
    #                              if key in fields_to_display and value is not None}

    #             # 필터링된 데이터를 텍스트로 구성
    #             pattern_text = "\n".join([f"{key}: {value}" for key, value in filtered_data.items()])

    #             # 직사각형 추가
    #             if pattern_text:  # 표시할 데이터가 있을 때만 추가
    #                 plt.gca().add_patch(plt.Rectangle((x - rect_width / 2, y - rect_height / 2), rect_width, rect_height,
    #                                                   color='lightgreen', alpha=0.5))
    #                 # 직사각형 안에 텍스트 추가
    #                 plt.text(x, y, pattern_text, ha='center', va='center', fontsize=8, color='black', wrap=True)
    #             break  # 매칭된 값이 표시되면 반복 종료

    # # 레전드를 위한 ProxyArtist 생성
    # legend_handles = []
    # for node, label in legend_labels.items():
    #     legend_handles.append(Line2D([0], [0], marker='o', color='w', label=f"{node}: {label}",
    #                                  markerfacecolor='skyblue', markersize=10))

    # # 레전드 추가
    # plt.legend(handles=legend_handles, loc="upper center", fontsize=10)

    # 타이틀 설정
    plt.title("Transaction Network Graph with Selected Fabric Data", fontsize=16)

    # 레이아웃 조정 (타이틀이 잘리는 경우 해결)
    plt.tight_layout(pad=2.0)

    plt.savefig("./test2.png", bbox_inches='tight')
    plt.show()

# 실행
order_id = '1'  # 여기서 orderId를 설정 (입력 값으로 받아도 됩니다)
transactions = fetch_transactions(order_id)  # Elasticsearch에서 해당 orderId의 트랜잭션만 가져오기
fabric_data = fetch_fabric_data(order_id)  # Elasticsearch에서 해당 orderId의 Fabric 데이터 가져오기
network_graph, order_dict, legend_labels, edge_labels = create_network_graph(transactions)  # 네트워크 그래프 생성
visualize_graph(network_graph, order_dict, legend_labels, edge_labels, fabric_data)  # 네트워크 그래프 시각화
