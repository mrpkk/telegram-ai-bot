from fastapi import APIRouter, Depends, HTTPException
from app.services.blockchains.ethereum import EthereumClient
from app.services.blockchains.solana import SolanaClient
from app.services.blockchains.ton import TONClient
from app.services.blockchains.cosmos import CosmosClient
from app.services.blockchains.sui import SuiClient
from app.services.blockchains.aptos import AptosClient

router = APIRouter()

@router.get("/ethereum/balance/{address}")
async def get_ethereum_balance(address: str):
    client = EthereumClient()
    balance = await client.get_balance(address)
    return {"balance": balance}

@router.get("/solana/balance/{address}")
async def get_solana_balance(address: str):
    client = SolanaClient()
    balance = await client.get_balance(address)
    return {"balance": balance}

@router.get("/ton/balance/{address}")
async def get_ton_balance(address: str):
    client = TONClient()
    balance = await client.get_balance(address)
    return {"balance": balance}

@router.get("/cosmos/balance/{address}")
async def get_cosmos_balance(address: str):
    client = CosmosClient()
    balance = await client.get_balance(address)
    return {"balance": balance}

@router.get("/sui/balance/{address}")
async def get_sui_balance(address: str):
    client = SuiClient()
    balance = await client.get_balance(address)
    return {"balance": balance}

@router.get("/aptos/balance/{address}")
async def get_aptos_balance(address: str):
    client = AptosClient()
    balance = await client.get_balance(address)
    return {"balance": balance}