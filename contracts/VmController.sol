// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VMController {

    struct VMConfig {
        bool exists;
        string vmName;
        string remote;
        string hook;
        string ipv4;
        string ipv4Gateway;
        uint256 port;
        bool tls;
        string sshKey;
        string sshAuthenticator;
    }

    mapping(string => VMConfig) public vmConfigs;

    event VMCreated(string vmName);
    event VMDestroyed(string vmName);

    function createVM(
        string memory vmName,
        string memory remote,
        string memory hook,
        string memory ipv4,
        string memory ipv4Gateway,
        uint256 port,
        bool tls,
        string memory sshKey,
        string memory sshAuthenticator
    ) external {
        require(!vmConfigs[vmName].exists, "VM already exists");

        vmConfigs[vmName] = VMConfig(
            true,
            vmName,
            remote,
            hook,
            ipv4,
            ipv4Gateway,
            port,
            tls,
            sshKey,
            sshAuthenticator
        );

        emit VMCreated(vmName);
    }

    function destroyVM(string memory vmName) external {
        require(vmConfigs[vmName].exists, "VM does not exist");

        delete vmConfigs[vmName];

        emit VMDestroyed(vmName);
    }
}
