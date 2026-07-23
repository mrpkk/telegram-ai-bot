const hre = require("hardhat");

async function main() {
  const MAIA = await hre.ethers.getContractFactory("MAIA");
  const maia = await MAIA.deploy();
  await maia.deployed();
  console.log("MAIA deployed to:", maia.address);

  const DAO = await hre.ethers.getContractFactory("DAO");
  const dao = await DAO.deploy(maia.address);
  await dao.deployed();
  console.log("DAO deployed to:", dao.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});