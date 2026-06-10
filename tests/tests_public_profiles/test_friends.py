from galaxy.api.types import UserInfo
from galaxy.api.errors import AuthenticationRequired
import pytest


@pytest.mark.asyncio
async def test_not_authenticated(plugin):
    with pytest.raises(AuthenticationRequired):
        await plugin.get_friends()


@pytest.mark.asyncio
async def test_no_friends(authenticated_plugin, steam_http_client, steam_id):
    steam_http_client.get_friends.return_value = []

    assert [] == await authenticated_plugin.get_friends()
    steam_http_client.get_friends.assert_called_once_with(steam_id)


@pytest.mark.asyncio
async def test_multiple_friends(authenticated_plugin, steam_http_client, steam_id):
    steam_http_client.get_friends.return_value = [
        UserInfo("76561198040630463","crak","avatar","profile"),
        UserInfo("76561198053830887","Danpire","avatar2","profile2")
        ]


    result = await authenticated_plugin.get_friends()
    assert result == [
        UserInfo("76561198040630463","crak","avatar","profile"),
        UserInfo("76561198053830887","Danpire","avatar2","profile2")
    ]
    steam_http_client.get_friends.assert_called_once_with(steam_id)
