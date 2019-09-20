from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from upvest.clientele import UpvestClienteleAPI

from .utils import ETH_ASSET_ID, get_app_api


class WalletUser(AbstractUser):

    wallet_id = models.CharField(null=True, max_length=50)

    def get_user_api(self):
        return UpvestClienteleAPI(
            settings.UPVEST_OAUTH_CLIENT_ID,
            settings.UPVEST_OAUTH_CLIENT_SECRET,
            self.username,
            self.password,
            user_agent=settings.UPVEST_USER_AGENT,
            base_url=settings.UPVEST_BACKEND,
        )

    @property
    def wallet(self):
        return self.get_user_api().wallets.get(self.wallet_id)

    @property
    def balance(self):
        # we have hardcoded this to only have one single asset type of ETH
        # so we can just return the first object...
        balance = self.wallet.balances[0]
        return Decimal(balance["amount"]) / (10 ** int(balance["exponent"]))

    def send(self, recipient, amount, fee):
        return self.wallet.transactions.create(self.password, ETH_ASSET_ID, amount, fee, recipient)

    def get_transactions(self, limit=None):
        if limit is None:
            return self.wallet.transactions.all()
        return self.wallet.transactions.list(limit)


def create_wallet(sender, instance, created, **kwargs):
    if not created:
        return

    api = get_app_api()
    api.users.create(instance.username, instance.password)

    api = instance.get_user_api()
    wallet = api.wallets.create(ETH_ASSET_ID, instance.password)
    instance.wallet_id = wallet.id
    instance.save()


post_save.connect(create_wallet, sender=WalletUser)
