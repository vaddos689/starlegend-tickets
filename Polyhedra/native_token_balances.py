from better_web3 import Chain
from better_web3.utils import write_lines
from eth_utils import from_wei
from loguru import logger
from eth_typing import ChecksumAddress


async def native_token_balances(ADDRESSES: list[ChecksumAddress]):
    if not ADDRESSES:
        logger.warning(f"There are no addresses!")
        return

    chain = Chain(rpc='https://opbnb-mainnet-rpc.bnbchain.org', symbol='BNB', use_eip1559=True, name='OpBNB')
    raw_balances = [raw_balance_data async for raw_balance_data in
                    chain.batch_request.balances(ADDRESSES, raise_exceptions=False)]

    balances_txt = "balances.txt"
    balances = []

    total_balance = 0
    for i, balance_data in enumerate(raw_balances, start=1):
        address = balance_data["address"]
        if "balance" in balance_data:
            balance = from_wei(balance_data["balance"], "ether")
            logger.info(f"[{i:03}] [{address}] {chain} {chain.token.symbol} {round(balance, 4)}")
            balances.append(f"{address}:{balance}")
            total_balance += balance
        else:
            exception = balance_data["exception"]
            logger.error(f"[{i:03}] [{address}] {chain} {exception}")
            balances.append(f"{address}:ERROR")

    logger.info(f'TOTAL BALANCE: {total_balance}')

    write_lines(balances_txt, balances)
