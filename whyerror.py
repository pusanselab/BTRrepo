from web3 import Web3

# Ganache 연결
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# 실패한 트랜잭션 해시
tx_hash = "0x97ed6962c1ce073768b9eb2a7dde1d1c053d54cc8ca325a0c061612d0e56cbf9"

# 트랜잭션 디버그 정보 호출
trace = w3.provider.make_request("debug_traceTransaction", [tx_hash])

# 출력된 트레이스 정보 확인
print(trace)
