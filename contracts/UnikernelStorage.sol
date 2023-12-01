// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UnikernelStorage {
    mapping(bytes32 => bytes) private unikernelData;

    event UnikernelStored(bytes32 indexed txHash, bytes unikernel);

    function storeUnikernel(bytes32 txHash, bytes memory unikernel) external {
        unikernelData[txHash] = unikernel;
        emit UnikernelStored(txHash, unikernel);
    }

    function getUnikernel(bytes32 txHash) external view returns (bytes memory) {
        return unikernelData[txHash];
    }
}
