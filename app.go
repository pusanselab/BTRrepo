/*
Copyright 2022 IBM All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
*/

package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"time"

	"github.com/hyperledger/fabric-gateway/pkg/client"
)

type SCEventInfo struct {
	SCName string `json:"scname"`
	TxID string `json:"txid"`
	Function string `json:"function"`
	Assetvalue map[string]interface{} `json:"assetvalue"`
}
const (
	channelName   = "mychannel"
	chaincodeName = "basic"
	smartcontractName = "dollartransfer"
)

// var now = time.Now()
// var assetID = fmt.Sprintf("asset%d", now.Unix()*1e3+int64(now.Nanosecond())/1e6)
// var input string
func main() {
	clientConnection := newGrpcConnection()
	defer clientConnection.Close()

	id := newIdentity()
	sign := newSign()

	gateway, err := client.Connect(
		id,
		client.WithSign(sign),
		client.WithClientConnection(clientConnection),
		client.WithEvaluateTimeout(5*time.Second),
		client.WithEndorseTimeout(15*time.Second),
		client.WithSubmitTimeout(5*time.Second),
		client.WithCommitStatusTimeout(1*time.Minute),
	)
	if err != nil {
		panic(err)
	}
	defer gateway.Close()

	network := gateway.GetNetwork(channelName)
	//contract := network.GetContractWithName(chaincodeName,smartcontractName)

	// Context used for event listening
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	//fmt.Printf("smart contract name : %s\n",contract.ContractName())
	// Listen for events emitted by subsequent transactions
	startChaincodeEventListening(ctx, network)

	//firstBlockNumber := createAsset(contract)
	// createAsset(contract)
	// updateAsset(contract)
	// transferAsset(contract)
	// deleteAsset(contract)
	select {}
	// Replay events from the block containing the first transaction
	//replayChaincodeEvents(ctx, network, firstBlockNumber)
}

func startChaincodeEventListening(ctx context.Context, network *client.Network) {
	fmt.Println("\n*** Start chaincode event listening")

	events, err := network.ChaincodeEvents(ctx, chaincodeName)
	if err != nil {
		panic(fmt.Errorf("failed to start chaincode event listening: %w", err))
	}

	go func() {
		for event := range events {
			asset := formatJSON(event.Payload)
			fmt.Printf("\n<-- Chaincode event(transaction id : %s) received: %s - %s\n",event.TransactionID, event.EventName, asset)
			var assetdata map[string]interface{}
			err := json.Unmarshal([]byte(asset), &assetdata)
			if err!= nil {
				fmt.Println(err)
				return
			}
			jsonfile := SCEventInfo {
				TxID: event.TransactionID,
				Function: event.EventName,
				Assetvalue: assetdata,
				SCName: "code_permission",
			}
			f,err := os.OpenFile("/shared_data/contract.log",os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
			if err != nil{
				fmt.Println(err)
			}
			saveJson(f,jsonfile)
			defer f.Close()
		}
	}()
	
}
func saveJson(filename *os.File, key interface{}){
	encodeJson := json.NewEncoder(filename)
	err := encodeJson.Encode(key)
	if err != nil{
		fmt.Println(err)
		return
	}
}
func formatJSON(data []byte) string {
	var result bytes.Buffer
	if err := json.Indent(&result, data, "", "  "); err != nil {
		panic(fmt.Errorf("failed to parse JSON: %w", err))
	}
	return result.String()
}

// func createAsset(contract *client.Contract) uint64 {
// 	fmt.Printf("\n--> Submit transaction: CreateAsset, %s owned by Sam KB bank 1000 won\n", assetID)

// 	_, commit, err := contract.SubmitAsync("CreateAsset", client.WithArguments(assetID, "Sam", "1000", "KB"))
// 	if err != nil {
// 		panic(fmt.Errorf("failed to submit transaction: %w", err))
// 	}

// 	status, err := commit.Status()
// 	if err != nil {
// 		panic(fmt.Errorf("failed to get transaction commit status: %w", err))
// 	}

// 	if !status.Successful {
// 		panic(fmt.Errorf("failed to commit transaction with status code %v", status.Code))
// 	}

// 	fmt.Println("\n*** CreateAsset committed successfully")

// 	return status.BlockNumber
// }

// func updateAsset(contract *client.Contract) {
// 	fmt.Printf("\n--> Submit transaction: UpdateAsset, %s update appraised value to 200\n", assetID)

// 	_, err := contract.SubmitTransaction("UpdateAsset", assetID, "Sam", "200", "Toss")
// 	if err != nil {
// 		panic(fmt.Errorf("failed to submit transaction: %w", err))
// 	}

// 	fmt.Println("\n*** UpdateAsset committed successfully")
// }

// func readAsset(contract *client.Contract) {
// 	fmt.Printf("\n--> Submit transaction: ReadAsset, %s \n", assetID)

// 	_, err := contract.SubmitTransaction("ReadAsset", assetID)
// 	if err != nil {
// 		panic(fmt.Errorf("failed to submit transaction: %w", err))
// 	}

// 	fmt.Println("\n*** ReadAsset committed successfully")
// }

// func deleteAsset(contract *client.Contract) {
// 	fmt.Printf("\n--> Submit transaction: DeleteAsset, %s\n", assetID)

// 	_, err := contract.SubmitTransaction("DeleteAsset", assetID)
// 	if err != nil {
// 		panic(fmt.Errorf("failed to submit transaction: %w", err))
// 	}

// 	fmt.Println("\n*** DeleteAsset committed successfully")
// }

// func replayChaincodeEvents(ctx context.Context, network *client.Network, startBlock uint64) {
// 	fmt.Println("\n*** Start chaincode event replay")

// 	events, err := network.ChaincodeEvents(ctx, chaincodeName, client.WithStartBlock(startBlock))
// 	if err != nil {
// 		panic(fmt.Errorf("failed to start chaincode event listening: %w", err))
// 	}

// 	for {
// 		select {
// 		case <-time.After(10 * time.Second):
// 			panic(errors.New("timeout waiting for event replay"))

// 		case event := <-events:
// 			asset := formatJSON(event.Payload)
// 			fmt.Printf("\n<-- Chaincode event replayed: %s - %s\n", event.EventName, asset)

// 			if event.EventName == "DeleteAsset" {
// 				// Reached the last submitted transaction so return to stop listening for events
// 				return
// 			}
// 		}
// 	}
// }
