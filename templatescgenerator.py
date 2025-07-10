import yaml

# Solidity 스마트 컨트랙트 템플릿 (CRUD 포함)
solidity_contract_template = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

contract {contract_name} {{
    struct Asset {{
        string id;
{fields}
    }}

    mapping(string => Asset) public assets;

    // Create Asset
    function createAsset(string memory _id{params}) public {{
        assets[_id] = Asset(_id{values});
    }}

    // Read Asset
    function getAsset(string memory _id) public view returns ({return_params}) {{
        Asset memory asset = assets[_id];
        return ({return_values});
    }}

    // Update Asset
    function updateAsset(string memory _id{params}) public {{
        require(bytes(assets[_id].id).length != 0, "Asset does not exist");
        assets[_id] = Asset(_id{values});
    }}

    // Delete Asset
    function deleteAsset(string memory _id) public {{
        require(bytes(assets[_id].id).length != 0, "Asset does not exist");
        delete assets[_id];
    }}
}}
"""

# Hyperledger Fabric 체인코드 템플릿 (CRUD 포함)
go_contract_template = """
package chaincode

import (
    "encoding/json"
    "fmt"
    "github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type SmartContract struct {{
    contractapi.Contract
}}

type Asset struct {{
{fields}
}}

// Create Asset
func (s *SmartContract) CreateAsset(ctx contractapi.TransactionContextInterface, id string{params}) error {{
    exists, err := s.AssetExists(ctx, id)
    if err != nil {{
        return err
    }}
    if exists {{
        return fmt.Errorf("the asset %s already exists", id)
    }}

    asset := Asset{{
        {values}
    }}
    assetJSON, err := json.Marshal(asset)
    if err != nil {{
        return err
    }}
    err = ctx.GetStub().SetEvent("CreateAsset", assetJSON)
	if err != nil {{
		return fmt.Errorf("failed to set event: %v", err)
	}}
    return ctx.GetStub().PutState(id, assetJSON)
}}

// Read Asset
func (s *SmartContract) ReadAsset(ctx contractapi.TransactionContextInterface, id string) (*Asset, error) {{
    assetJSON, err := ctx.GetStub().GetState(id)
    if err != nil {{
        return nil, fmt.Errorf("failed to read from world state: %v", err)
    }}
    if assetJSON == nil {{
        return nil, fmt.Errorf("the asset %s does not exist", id)
    }}

    var asset Asset
    err = json.Unmarshal(assetJSON, &asset)
    if err != nil {{
        return nil, err
    }}
    
    return &asset, nil
}}

// Update Asset
func (s *SmartContract) UpdateAsset(ctx contractapi.TransactionContextInterface, id string{params}) error {{
    exists, err := s.AssetExists(ctx, id)
    if err != nil {{
        return err
    }}
    if !exists {{
        return fmt.Errorf("the asset %s does not exist", id)
    }}

    asset := Asset{{
        {values}
    }}
    assetJSON, err := json.Marshal(asset)
    if err != nil {{
        return err
    }}
    err = ctx.GetStub().SetEvent("UpdateAsset", assetJSON)
	if err != nil {{
		return fmt.Errorf("failed to set event: %v", err)
	}}

    return ctx.GetStub().PutState(id, assetJSON)
}}

// Delete Asset
func (s *SmartContract) DeleteAsset(ctx contractapi.TransactionContextInterface, id string) error {{
    exists, err := s.AssetExists(ctx, id)
    if err != nil {{
        return err
    }}
    if !exists {{
        return fmt.Errorf("the asset %s does not exist", id)
    }}
    assetJSON, err := ctx.GetStub().GetState(id)
    if err != nil {{
        return err
    }}
    // Delete event
    err = ctx.GetStub().SetEvent("DeleteAsset", assetJSON)
    if err != nil {{
        return fmt.Errorf("failed to set event: %v", err)
    }}
    return ctx.GetStub().DelState(id)
}}

// AssetExists checks if an asset exists in the world state
func (s *SmartContract) AssetExists(ctx contractapi.TransactionContextInterface, id string) (bool, error) {{
    assetJSON, err := ctx.GetStub().GetState(id)
    if err != nil {{
        return false, fmt.Errorf("failed to read from world state: %v", err)
    }}
    

    
    return assetJSON != nil, nil
}}
"""

# YAML 파일을 읽고 데이터 구조에 맞는 컨트랙트 생성
def generate_smart_contracts_from_yaml(yaml_file):
    try:
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
    except Exception as e:
        print(f"YAML 파일을 읽는 중 오류 발생: {e}")
        return
    
    # Ethereum용 스마트 컨트랙트 생성
    if 'ethereum' in data:
        for contract_name, attributes in data['ethereum'].items():
            solidity_code = generate_solidity_contract(contract_name, attributes)
            with open(f'{contract_name}.sol', 'w') as sol_file:
                sol_file.write(solidity_code)
            print(f'Ethereum 스마트 컨트랙트({contract_name}.sol)가 생성되었습니다.')
    
    # Hyperledger Fabric용 체인코드 생성
    if 'hlf' in data:
        for contract_name, attributes in data['hlf'].items():
            go_code = generate_go_contract(contract_name, attributes)
            with open(f'{contract_name}.go', 'w') as go_file:
                go_file.write(go_code)
            print(f'Hyperledger Fabric 체인코드({contract_name}.go)가 생성되었습니다.')

# Solidity 스마트 컨트랙트 생성 함수
def generate_solidity_contract(contract_name, attributes):
    fields = "\n".join([f"        {convert_solidity_type(attr['type'], True)} {attr['name']};" for attr in attributes])
    params = "".join([f", {convert_solidity_type(attr['type'], False)} _{attr['name']}" for attr in attributes])
    values = "".join([f", _{attr['name']}" for attr in attributes])
    return_params = ", ".join([f"{convert_solidity_type(attr['type'], False)}" for attr in attributes])
    return_values = ", ".join([f"asset.{attr['name']}" for attr in attributes])

    return solidity_contract_template.format(
        contract_name=contract_name.capitalize(),
        fields=fields,
        params=params,
        values=values,
        return_params=return_params,
        return_values=return_values
    )

# Hyperledger Fabric 체인코드 생성 함수
def generate_go_contract(contract_name, attributes):
    fields = "\n".join([f"    {attr['name'].capitalize()} {convert_go_type(attr['type'])} `json:\"{attr['name']}\"`" for attr in attributes])
    params = "".join([f", {attr['name']} {convert_go_type(attr['type'])}" for attr in attributes])
    values = "".join([f"\n        {attr['name'].capitalize()}: {attr['name']}," for attr in attributes])

    return go_contract_template.format(
        fields=fields,
        params=params,
        values=values
    )

# 타입 변환 함수
def convert_solidity_type(yaml_type,is_field):
    if is_field:
        return {
        'string': 'string',
        'int': 'uint',
        'bool': 'bool',
        }.get(yaml_type, 'string')
    else:
        return {
        'string': 'string memory',
        'int': 'uint',
        'bool': 'bool',
    }.get(yaml_type, 'string')

def convert_go_type(yaml_type):
    return {
        'string': 'string',
        'int': 'int',
        'bool': 'bool',
    }.get(yaml_type, 'string')  # 기본적으로 string으로 처리

# 예시 YAML 파일 경로
yaml_file = 'data.yaml'

# 스마트 컨트랙트 생성
generate_smart_contracts_from_yaml(yaml_file)
