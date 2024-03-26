from eth_utils import to_hex
from loguru import logger
from pyuseragents import random
from core.info import scans
from core.utils import Account
from Polyhedra.info import (
    claim_ticket_address, ticket_abi, operator_address,operator_abi
)
from better_web3.utils import sign_message
import json


class Polyhedra(Account):
    def __init__(self, key, id, address_to=None, proxy=None, chain=None):
        super().__init__(key, id=id, address_to=address_to, proxy=proxy, chain=chain)
        self.contract = self.get_contract(claim_ticket_address, ticket_abi)
        self.operator_contract = self.get_contract(operator_address, operator_abi)

        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'origin': 'https://star.legend.game',
            'referer': 'https://star.legend.game/',
            'user-agent': random(),
        }

    async def validation_message(self):
        json = {
            'publicKey': self.address
        }

        try:
            data = await self.send_request(
                f'https://api.legend.game/api/signin/validation_message',
                'POST',
                headers=self.headers,
                json=json
            )
            return data['message']

        except Exception as e:
            logger.error(f'{self.acc_info} - validation message error')

    async def signin(self, signed_message):
        json = {
            'publicKey': self.address,
            'signedMessage': signed_message
        }

        try:
            data = await self.send_request(
                f'https://api.legend.game/api/signin',
                'POST',
                headers=self.headers,
                json=json
            )
            return data['token']

        except Exception as e:
            logger.error(f'{self.acc_info} - signin error')

    async def fetch_tickets(self):
        # message = await self.validation_message()
        # signed_message = sign_message(message, self.account)
        # bearer_token = await self.signin(signed_message)
        balance = await self.contract.functions.balanceOf(self.address, 0).call()
        logger.info(f'{self.acc_info} - TICKETS: {balance}')

    async def mint_ticket(self):
        tx = await self.build_tx(self.contract, 'mint')
        if not tx: return
        data = await self.sign_and_send(tx)
        if not data: return
        status, hash_ = data
        if status:
            logger.success(
                f'{self.acc_info} - успешно сминтил Daily ticket\ntx: {scans['opbnb']}{to_hex(hash_)}')
            await self.sleep_indicator(f'{self.acc_info}:')
            return True
        else:
            logger.error(f'{self.acc_info} - транзакция не успешна...')
            return False

    async def approve_all_tickets(self):
        tx = await self.build_tx(self.contract, 'setApprovalForAll', args=(operator_address, True))
        if not tx: return
        data = await self.sign_and_send(tx)
        if not data: return
        status, hash_ = data
        if status:
            logger.info(
                f'{self.acc_info} - апрувнул все тикеты\ntx: {scans['opbnb']}{to_hex(hash_)}')
            await self.sleep_indicator(f'{self.acc_info}:')
            return True
        else:
            logger.error(f'{self.acc_info} - транзакция не успешна...')
            return False

    async def summon_10_tickets(self):
        tx = await self.build_tx(self.contract, 'commit', args=(operator_address, True))
        if not tx: return
        data = await self.sign_and_send(tx)
        if not data: return
        status, hash_ = data
        if status:
            logger.info(
                f'{self.acc_info} - апрувнул все тикеты\ntx: {scans['opbnb']}{to_hex(hash_)}')
            await self.sleep_indicator(f'{self.acc_info}:')
            return True
        else:
            logger.error(f'{self.acc_info} - транзакция не успешна...')
            return False

    # async def get_claimable_amount(self):
    #     data = await self.get_proof()
    #     if not data:
    #         logger.error(f'{self.acc_info} - не элиджбл для клейма ZK')
    #         return 0
    #
    #     for chain in data:
    #         amount = data[chain][0] / 10 ** 18
    #         logger.success(f'{self.address}:{chain} - элидбжл {amount} ZK')
    #         return amount

    # async def claim(self):
    #     data = await self.get_proof()
    #     if not data:
    # #         logger.error(f'{self.acc_info} - не элиджбл для клейма ZK')
    #         return
    #     if self.chain not in data:
    #         logger.error(f'{self.acc_info} - не элиджбл для клейма ZK')
    #         return
    #
    #     amount, index, proof = data[self.chain]
    #     tx = await self.build_tx(self.contract, 'claim', args=(index, self.address, amount, proof))
    #     if not tx: return
    #     data = await self.sign_and_send(tx)
    #     if not data: return
    #     status, hash_ = data
    #     if status:
    #         logger.success(
    #             f'{self.acc_info} - успешно заклеймил {amount / 10 ** 18} ZK\ntx: {scans[self.chain]}{to_hex(hash_)}')
    #         await self.sleep_indicator(f'{self.acc_info}:')
    #         return True
    #     else:
    #         logger.error(f'{self.acc_info} - транзакция не успешна...')
    #         return False
