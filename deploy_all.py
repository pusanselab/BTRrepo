import os
import subprocess
import shutil

# 경로 설정
base_dir = os.path.dirname(os.path.abspath(__file__))
eth_contract_src = os.path.join(base_dir, 'commiting_code.sol')
eth_project_dir = os.path.join(base_dir, '..', 'etherpj')
eth_contract_dest = os.path.join(eth_project_dir, 'contracts', 'commiting_code.sol')
fabric_base_dir =  os.path.dirname(base_dir)
fabric_chaincode_src = os.path.join(base_dir, 'code_permission.go')
fabric_chaincode_dest = os.path.join(fabric_base_dir, 'fabric-samples', 'asset-transfer-basic', 'chaincode-go', 'chaincode', 'smartcontract.go')

# Ethereum 스마트 컨트랙트를 Truffle 프로젝트 경로로 복사
def deploy_ethereum_contract():
    print("Ethereum 컨트랙트 복사 중...")
    try:
        # 기존 파일이 있으면 삭제
        if os.path.exists(eth_contract_dest):
            os.remove(eth_contract_dest)
        
        # 스마트 컨트랙트 파일 복사
        shutil.copy(eth_contract_src, eth_contract_dest)
        print(f"컨트랙트가 {eth_contract_dest}로 복사되었습니다.")
        
        # Truffle 마이그레이션 실행
        os.chdir(eth_project_dir)  # Truffle 프로젝트 디렉토리로 이동
        print("Truffle 마이그레이션 실행 중...")
        subprocess.run(["truffle", "migrate", "--reset"], check=True)
        print("Ethereum 컨트랙트 배포 완료.")
    except Exception as e:
        print(f"Ethereum 배포 중 에러 발생: {str(e)}")

# Hyperledger Fabric 체인코드를 지정된 경로로 복사 후 배포
def deploy_fabric_chaincode():
    print("Fabric 체인코드 복사 중...")
    try:
        # 기존 파일이 있으면 삭제
        if os.path.exists(fabric_chaincode_dest):
            os.remove(fabric_chaincode_dest)
        
        # 체인코드 파일 복사
        shutil.copy(fabric_chaincode_src, fabric_chaincode_dest)
        print(f"체인코드가 {fabric_chaincode_dest}로 복사되었습니다.")
        
        # Hyperledger Fabric 배포 명령 (예시: 개발 네트워크 기준)
        print("Hyperledger Fabric 배포 중...")
        os.chdir(os.path.dirname(os.path.dirname(fabric_chaincode_dest)))
        subprocess.run(['go', 'env', '-w', 'GO111MODULE=on'], check=True)
        subprocess.run(['go', 'mod', 'vendor'], check=True)

        os.chdir(os.path.join(base_dir, '..', 'fabric-samples', 'test-network'))
        subprocess.run(["./network.sh", "deployCC", "-ccn", "basic", "-ccp", os.path.dirname(os.path.dirname(fabric_chaincode_dest))+"/", "-ccl", "go"], check=True)
        print("Hyperledger Fabric 체인코드 배포 완료.")
    except Exception as e:
        print(f"Fabric 배포 중 에러 발생: {str(e)}")

if __name__ == "__main__":
    #deploy_ethereum_contract()
    deploy_fabric_chaincode()
