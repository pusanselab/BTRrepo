from elasticsearch import Elasticsearch

# Elasticsearch 클라이언트 초기화
es = Elasticsearch(hosts=["http://localhost:9200"])

# 인덱스 이름 설정
index_name = "hyperledgerfabric"

# 패턴 데이터 정의
pattern1 = {
    "request_loc": "OrgMSP2",
    "email": "john@example.com",
    "name": "John",
    "order_id": "1",
    "phone": "555-1234"
}

pattern2 = {
    "request_loc": "OrgMSP3",
    "address": "123 Main St",
    "name": "John",
    "order_id": "1",
    "phone": "555-1234"
}

# Elasticsearch에 문서 삽입
responses = []
for pattern in [pattern1, pattern2]:
    response = es.index(index=index_name, document=pattern)
    responses.append(response)

# 결과 출력
for i, response in enumerate(responses):
    print(f"Document {i + 1} Response:", response)
document1 = es.get(index="hyperledgerfabric", id='t69J95MBkLbaaYnX-KWT')
print("Document 1:", document1)

# 문서 조회 (두 번째 문서)
document2 = es.get(index="hyperledgerfabric", id='uK9J95MBkLbaaYnX-aWO')
print("Document 2:", document2)