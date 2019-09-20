from django.conf import settings
from upvest.tenancy import UpvestTenancyAPI

ETH_ASSET_ID = "deaaa6bf-d944-57fa-8ec4-2dd45d1f5d3f"


def get_app_api():
    return UpvestTenancyAPI(
        settings.UPVEST_API_KEY_ID,
        settings.UPVEST_API_KEY_SECRET,
        settings.UPVEST_API_KEY_PASSPHRASE,
        user_agent=settings.UPVEST_USER_AGENT,
        base_url=settings.UPVEST_BACKEND,
    )
