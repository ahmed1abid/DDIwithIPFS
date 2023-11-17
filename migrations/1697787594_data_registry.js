const DataRegistry = artifacts.require("DataRegistry");

module.exports = function(deployer) {
  deployer.deploy(DataRegistry);
};
