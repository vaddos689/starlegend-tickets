import asyncio
import sys
from typing import Type
import questionary
from questionary import Choice
from loguru import logger
from Polyhedra.polyhedra import Polyhedra
from core.other_info import get_batches
from core.other_info import keys
from better_web3 import Wallet
from Polyhedra.native_token_balances import native_token_balances


async def main(module):
    if module == 'native_token_balances':
        addresses = []
        for key in keys:
            addresses.append(Wallet.from_key(key).address)
        await native_token_balances(addresses)
        logger.success('Балансы OPBNB получены и записаны в файл balances.txt')

    if module == 'mint_tickets':
        for batch in get_batches():
            tasks = []
            for key in batch:
                key_data = key.split(';')
                key = key_data[1]
                polyhedra = Polyhedra(key=key_data[1], id=key_data[0])
                tasks.append(polyhedra.mint_ticket())
            reses = await asyncio.gather(*tasks)

    if module == 'tickets_balances':
        for batch in get_batches():
            tasks = []
            for key in batch:
                key_data = key.split(';')
                polyhedra = Polyhedra(key=key_data[1], id=key_data[0])
                tasks.append(polyhedra.fetch_tickets())
            reses = await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        module = questionary.select(
            "Выберите модуль для работы...",
            choices=[
                Choice(" 1) OPBNB BALANCES 🏦", 'native_token_balances'),
                Choice(" 2) MINT TICKETS 🎫", 'mint_tickets'),
                Choice(" 3) TICKETS BALANCES", 'tickets_balances'),
                Choice(" 4) ВЫХОД", 'exit'),
            ],
            qmark="",
            pointer="⟹",
        ).ask()
        if module == 'exit':
            loop.close()
            sys.exit()
        loop.run_until_complete(main(module))