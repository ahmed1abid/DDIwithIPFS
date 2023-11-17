// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

contract DataRegistry {
  
    string public storedData;

    function storeData(string memory newData) public {
        storedData = newData;
    }

    function getStoredData() public view returns (string memory) {
        return storedData;
    }


}
