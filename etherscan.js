const fs = require('fs');
const {Web3} = require('web3');

const web3 = new Web3(new Web3.providers.WebsocketProvider('ws://127.0.0.1:8545')); // Ganache 네트워크에 연결

const contractABI = [{
    "inputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "name": "assets",
    "outputs": [
      {
        "internalType": "string",
        "name": "id",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "content",
        "type": "string"
      },
      {
        "internalType": "uint256",
        "name": "likes",
        "type": "uint256"
      },
      {
        "internalType": "string",
        "name": "timestamp",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function",
    "constant": true
  },
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "_id",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "_content",
        "type": "string"
      },
      {
        "internalType": "uint256",
        "name": "_likes",
        "type": "uint256"
      },
      {
        "internalType": "string",
        "name": "_timestamp",
        "type": "string"
      }
    ],
    "name": "createAsset",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "_id",
        "type": "string"
      }
    ],
    "name": "getAsset",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      },
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      },
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function",
    "constant": true
  },
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "_id",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "_content",
        "type": "string"
      },
      {
        "internalType": "uint256",
        "name": "_likes",
        "type": "uint256"
      },
      {
        "internalType": "string",
        "name": "_timestamp",
        "type": "string"
      }
    ],
    "name": "updateAsset",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "_id",
        "type": "string"
      }
    ],
    "name": "deleteAsset",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }]; // 컴파일된 스마트 컨트랙트 ABI
const contractAddress = '0xa1D5b5dCe587E97A992Bc70717FFE75a2579C7c1'; // 스마트 컨트랙트 주소

// 스마트 컨트랙트 인스턴스 생성
const contract = new web3.eth.Contract(contractABI, contractAddress);

const fromBlock = 0; // 조회를 시작할 블록 번호
const toBlock = 'latest'; // 최신 블록까지 조회

async function getAllTransactionReceipts() {
    try {
        const latestBlock = await web3.eth.getBlockNumber(); // 최신 블록 번호 가져오기
        const endBlock = toBlock === 'latest' ? latestBlock : toBlock;
        const etherdata = []
        // fromBlock에서 toBlock까지 블록을 순차적으로 가져옴
        for (let i = fromBlock; i <= endBlock; i++) {
            const block = await web3.eth.getBlock(i, true); // true는 트랜잭션을 포함시킨다는 옵션
            //console.log(`블록 번호: ${i}`);
            
            if (block && block.transactions.length > 0) {
                for (const tx of block.transactions) {
                    //console.log(`트랜잭션 해시: ${tx.hash}`);

                    // 트랜잭션 영수증을 가져옴
                    const receipt = await web3.eth.getTransaction(tx.hash);
                    // console.log('트랜잭션 영수증:', receipt);
                    const methodSignature = tx.input.slice(0, 10);
                    // ABI에서 함수 서명을 매칭하여 함수 정의 찾기
                    const method = contract.options.jsonInterface.find(
                        (method) => methodSignature === web3.eth.abi.encodeFunctionSignature(method)
                    );
                    if (method) {
                        // 함수 인자 디코딩
                        const params = web3.eth.abi.decodeParameters(method.inputs, tx.input.slice(10));
                        // console.log(`함수 이름: ${method.name}`);
                        // console.log('인자:', params);
                        const jsonData = {
                            assetid: params._id, // _id 파라미터가 있을 경우 가져옵니다
                            from: tx.from,
                            to: tx.to,
                            method: method.name
                        };
                        etherdata.push(jsonData)
                        console.log('트랜잭션 정보:', JSON.stringify(jsonData, null, 2));
                    } else {
                        console.log('해당하는 함수 서명이 ABI에서 발견되지 않았습니다.');
                    }
                }
            } else {
                console.log('트랜잭션이 없는 블록입니다.');
            }
        }
        fs.writeFileSync('./transactions_data.json', JSON.stringify(etherdata, null, 2), 'utf8');
        console.log('모든 트랜잭션 정보가 transactions_data.json 파일에 저장되었습니다.');
        
    } catch (error) {
        console.error('트랜잭션 영수증 가져오는 중 오류 발생:', error);
    } finally {
        // WebSocket 연결 종료
        web3.currentProvider.disconnect();
        console.log('WebSocket 연결이 종료되었습니다.');
    }
    
}

getAllTransactionReceipts();
  