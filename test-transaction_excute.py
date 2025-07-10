from web3 import Web3
import time
# 트랜잭션 정보 출력 함수
from eth_abi import decode
from eth_abi.exceptions import DecodingError
from elasticsearch import Elasticsearch
from datetime import datetime

# Elasticsearch 클라이언트 설정
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])  # Elasticsearch의 주소와 포트

# 트랜잭션 정보 출력 및 저장 함수
def analyze_transaction(tx_hash, contract_abi):
    # 트랜잭션 및 영수증 가져오기
    tx = web3.eth.get_transaction(tx_hash)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    # print(f"From: {tx['from']}")
    # print(f"To: {tx['to']}")
    
    # ABI 디코더 생성
    contract = web3.eth.contract(address=tx['to'], abi=contract_abi)

    # 함수와 인수 디코딩
    try:
        func_obj, func_params = contract.decode_function_input(tx['input'])
        # print(f"Function Called: {func_obj.fn_name}")
        # print("Parameters:")
        # for key, value in func_params.items():
        #     print(f"  {key}: {value}")
        
        # 트랜잭션 데이터 저장
        transaction_data = {
            "from": tx['from'],
            "sc_address": tx['to'],
            "function_info": {
                "function_name": func_obj.fn_name,
                "parameters": func_params
            },
            "timestamp": datetime.utcfromtimestamp(web3.eth.get_block(tx['blockNumber'])['timestamp']).isoformat(),
            "to": next((func_params[key] for key in ['_seller', '_manufacturer', '_deliveryAgency'] if key in func_params and func_params[key]), None) 
            # "tx_hash": tx_hash,
            # "status": tx_receipt['status']  # 성공 여부
        }
        # Elasticsearch에 트랜잭션 저장
        es.index(index="transactions", document=transaction_data)
        print("Transaction data saved to Elasticsearch.")
    
    except DecodingError:
        print("Unable to decode function input.")
    # print("-" * 50)

# Ganache 설정
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# 계정 설정
accounts = web3.eth.accounts
customer = accounts[0]  # 주문자
seller = accounts[1]    # 판매사
manufacturer = accounts[2]  # 제조사
delivery_agency = accounts[3]  # 배송 대행사

# 배포된 컨트랙트 주소 및 ABI
# (중략 - ABI와 컨트랙트 주소는 기존과 동일)

# 배포된 컨트랙트 주소 및 ABI
order_contract_address = "0xea14ADD3691a3f05CEDC88D1B79c2a204555ccBe"  # OrderContract의 배포 주소
order_abi = """
[
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "orderId",
          "type": "uint256"
        }
      ],
      "name": "OrderFulfilled",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "orderId",
          "type": "uint256"
        },
        {
          "indexed": false,
          "internalType": "address",
          "name": "customer",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "address",
          "name": "seller",
          "type": "address"
        }
      ],
      "name": "OrderPlaced",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "orderCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "orders",
      "outputs": [
        {
          "internalType": "address",
          "name": "customer",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "seller",
          "type": "address"
        },
        {
          "internalType": "string",
          "name": "productName",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "quantity",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "price",
          "type": "uint256"
        },
        {
          "internalType": "bool",
          "name": "isFulfilled",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_orderId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "_seller",
          "type": "address"
        },
        {
          "internalType": "string",
          "name": "_productName",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "_quantity",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "_price",
          "type": "uint256"
        }
      ],
      "name": "placeOrder",
      "outputs": [],
      "stateMutability": "payable",
      "type": "function",
      "payable": true
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_orderId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "_seller",
          "type": "address"
        }
      ],
      "name": "fulfillOrder",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]
"""
manufacture_contract_address = "0x6eDe4b2349B9137c6B3A19993721A82FACDfF8A7"  # ManufactureContract의 배포 주소
manufacture_abi = """
[
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "orderId",
          "type": "uint256"
        }
      ],
      "name": "ManufactureCompleted",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "orderId",
          "type": "uint256"
        },
        {
          "indexed": false,
          "internalType": "address",
          "name": "manufacturer",
          "type": "address"
        }
      ],
      "name": "ManufactureRequested",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "manufactures",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "orderId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "manufacturer",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "seller",
          "type": "address"
        },
        {
          "internalType": "bool",
          "name": "isManufactured",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_orderId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "_manufacturer",
          "type": "address"
        }
      ],
      "name": "requestManufacture",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_orderId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "_seller",
          "type": "address"
        }
      ],
      "name": "completeManufacture",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]
"""

delivery_contract_address = "0x997D9A196d94804C98fD4B8eA27A8FFd443740b8"  # DeliveryContract의 배포 주소
delivery_abi = """
[
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "orderId",
          "type": "uint256"
        }
      ],
      "name": "DeliveryCompleted",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "orderId",
          "type": "uint256"
        },
        {
          "indexed": false,
          "internalType": "address",
          "name": "deliveryAgency",
          "type": "address"
        }
      ],
      "name": "DeliveryRequested",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "deliveries",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "orderId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "deliveryAgency",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "seller",
          "type": "address"
        },
        {
          "internalType": "bool",
          "name": "isShipped",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "isDelivered",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_orderId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "_deliveryAgency",
          "type": "address"
        }
      ],
      "name": "requestDelivery",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_orderId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "_seller",
          "type": "address"
        }
      ],
      "name": "completeDelivery",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]
"""  # DeliveryContract의 ABI

# 컨트랙트 인스턴스 생성
order_contract = web3.eth.contract(address=order_contract_address, abi=order_abi)
manufacture_contract = web3.eth.contract(address=manufacture_contract_address, abi=manufacture_abi)
delivery_contract = web3.eth.contract(address=delivery_contract_address, abi=delivery_abi)
# 주문 흐름 실행 (지연 전송 추가)
for order_id in range(1, 11):  # 1부터 10까지 반복
    # 주문자 -> 판매사 주문 생성
    product_name = "Product A"
    quantity = 1
    price = web3.to_wei(0.1, 'ether')
    
    order_tx = order_contract.functions.placeOrder(
        order_id,
        seller,
        product_name,
        quantity,
        price
    ).build_transaction({
        'from': customer,
        'value': price,
        'nonce': web3.eth.get_transaction_count(customer),
        'gas': 3000000
    })
    
    order_tx_hash = web3.eth.send_transaction(order_tx)
    tx_receipt = web3.eth.wait_for_transaction_receipt(order_tx_hash)
    analyze_transaction(order_tx_hash, order_abi)
    print(f"Order ID: {order_id} placed")

    # 3, 6, 9번은 지연 전송
    if order_id in [3, 6, 9]:
        print(f"Delaying order ID {order_id}...")
        time.sleep(5)  # 5초 지연

    # 판매사 -> 제조사 제조 요청
    manufacture_tx = manufacture_contract.functions.requestManufacture(
        order_id,
        manufacturer
    ).build_transaction({
        'from': seller,
        'nonce': web3.eth.get_transaction_count(seller),
        'gas': 3000000
    })
    manufacture_tx_hash = web3.eth.send_transaction(manufacture_tx)
    tx_receipt = web3.eth.wait_for_transaction_receipt(manufacture_tx_hash)
    analyze_transaction(manufacture_tx_hash, manufacture_abi)

    # 제조사 -> 제조 완료
    complete_manufacture_tx = manufacture_contract.functions.completeManufacture(
        order_id,
        seller
    ).build_transaction({
        'from': manufacturer,
        'nonce': web3.eth.get_transaction_count(manufacturer),
        'gas': 3000000
    })
    complete_manufacture_tx_hash = web3.eth.send_transaction(complete_manufacture_tx)
    tx_receipt = web3.eth.wait_for_transaction_receipt(complete_manufacture_tx_hash)
    analyze_transaction(complete_manufacture_tx_hash, manufacture_abi)

    # 판매사 -> 배송 대행사 요청
    delivery_tx = delivery_contract.functions.requestDelivery(
        order_id,
        delivery_agency
    ).build_transaction({
        'from': seller,
        'nonce': web3.eth.get_transaction_count(seller),
        'gas': 3000000
    })
    delivery_tx_hash = web3.eth.send_transaction(delivery_tx)
    tx_receipt = web3.eth.wait_for_transaction_receipt(delivery_tx_hash)
    analyze_transaction(delivery_tx_hash, delivery_abi)

    # 배송 대행사 -> 배송 완료
    complete_delivery_tx = delivery_contract.functions.completeDelivery(
        order_id,
        seller
    ).build_transaction({
        'from': delivery_agency,
        'nonce': web3.eth.get_transaction_count(delivery_agency),
        'gas': 3000000
    })
    complete_delivery_tx_hash = web3.eth.send_transaction(complete_delivery_tx)
    tx_receipt = web3.eth.wait_for_transaction_receipt(complete_delivery_tx_hash)
    analyze_transaction(complete_delivery_tx_hash, delivery_abi)

print("All orders processed successfully!")
