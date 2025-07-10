
package chaincode

import (
    "encoding/json"
    "fmt"
    "github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type SmartContract struct {
    contractapi.Contract
}

type Asset struct {
    Approvement bool `json:"approvement"`
    Approver string `json:"approver"`
}

// Create Asset
func (s *SmartContract) CreateAsset(ctx contractapi.TransactionContextInterface, id string, approvement bool, approver string) error {
    exists, err := s.AssetExists(ctx, id)
    if err != nil {
        return err
    }
    if exists {
        return fmt.Errorf("the asset %s already exists", id)
    }

    asset := Asset{
        
        Approvement: approvement,
        Approver: approver,
    }
    assetJSON, err := json.Marshal(asset)
    if err != nil {
        return err
    }
    err = ctx.GetStub().SetEvent("CreateAsset", assetJSON)
	if err != nil {
		return fmt.Errorf("failed to set event: %v", err)
	}
    return ctx.GetStub().PutState(id, assetJSON)
}

// Read Asset
func (s *SmartContract) ReadAsset(ctx contractapi.TransactionContextInterface, id string) (*Asset, error) {
    assetJSON, err := ctx.GetStub().GetState(id)
    if err != nil {
        return nil, fmt.Errorf("failed to read from world state: %v", err)
    }
    if assetJSON == nil {
        return nil, fmt.Errorf("the asset %s does not exist", id)
    }

    var asset Asset
    err = json.Unmarshal(assetJSON, &asset)
    if err != nil {
        return nil, err
    }
    
    return &asset, nil
}

// Update Asset
func (s *SmartContract) UpdateAsset(ctx contractapi.TransactionContextInterface, id string, approvement bool, approver string) error {
    exists, err := s.AssetExists(ctx, id)
    if err != nil {
        return err
    }
    if !exists {
        return fmt.Errorf("the asset %s does not exist", id)
    }

    asset := Asset{
        
        Approvement: approvement,
        Approver: approver,
    }
    assetJSON, err := json.Marshal(asset)
    if err != nil {
        return err
    }
    err = ctx.GetStub().SetEvent("UpdateAsset", assetJSON)
	if err != nil {
		return fmt.Errorf("failed to set event: %v", err)
	}

    return ctx.GetStub().PutState(id, assetJSON)
}

// Delete Asset
func (s *SmartContract) DeleteAsset(ctx contractapi.TransactionContextInterface, id string) error {
    exists, err := s.AssetExists(ctx, id)
    if err != nil {
        return err
    }
    if !exists {
        return fmt.Errorf("the asset %s does not exist", id)
    }
    assetJSON, err := ctx.GetStub().GetState(id)
    if err != nil {
        return err
    }
    // Delete event
    err = ctx.GetStub().SetEvent("DeleteAsset", assetJSON)
    if err != nil {
        return fmt.Errorf("failed to set event: %v", err)
    }
    return ctx.GetStub().DelState(id)
}

// AssetExists checks if an asset exists in the world state
func (s *SmartContract) AssetExists(ctx contractapi.TransactionContextInterface, id string) (bool, error) {
    assetJSON, err := ctx.GetStub().GetState(id)
    if err != nil {
        return false, fmt.Errorf("failed to read from world state: %v", err)
    }
    

    
    return assetJSON != nil, nil
}
