
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

contract Commiting_code {
    struct Asset {
        string id;
        string commiter;
        string contents;
        string timestamp;
    }

    mapping(string => Asset) public assets;

    // Create Asset
    function createAsset(string memory _id, string memory _commiter, string memory _contents, string memory _timestamp) public {
        assets[_id] = Asset(_id, _commiter, _contents, _timestamp);
    }

    // Read Asset
    function getAsset(string memory _id) public view returns (string memory, string memory, string memory) {
        Asset memory asset = assets[_id];
        return (asset.commiter, asset.contents, asset.timestamp);
    }

    // Update Asset
    function updateAsset(string memory _id, string memory _commiter, string memory _contents, string memory _timestamp) public {
        require(bytes(assets[_id].id).length != 0, "Asset does not exist");
        assets[_id] = Asset(_id, _commiter, _contents, _timestamp);
    }

    // Delete Asset
    function deleteAsset(string memory _id) public {
        require(bytes(assets[_id].id).length != 0, "Asset does not exist");
        delete assets[_id];
    }
}
