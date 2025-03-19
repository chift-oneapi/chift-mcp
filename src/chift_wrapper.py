import chift
from chift import Consumer

from src.config import config


class ChiftWrapper:
    def __init__(self) -> None:
        self._chift = chift
        self._chift.client_id = config.chift.client_id
        self._chift.client_secret = config.chift.client_secret
        self._chift.account_id = config.chift.account_id

    @property
    def consumer(self) -> Consumer:
        return self._chift.Consumer.get(config.chift.consumer_id)



chift_wrapper = ChiftWrapper()
