// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

contract DataRegistry {
  
    string public storedData;

    event FileStored(address indexed sender, string filePath);

    function storeData(string memory newData) public {
        storedData = newData;
    }

    function getStoredData() public view returns (string memory) {
        return storedData;
    }
    
    function storeFile(string memory filePath) public {
        emit FileStored(msg.sender, filePath);
    }
}
