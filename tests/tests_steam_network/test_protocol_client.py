import asyncio
from unittest.mock import MagicMock, AsyncMock, ANY
from typing import NamedTuple, List

import pytest

from galaxy.unittest.mock import async_return_value, skip_loop
from galaxy.api.errors import Banned, BackendNotAvailable
from steam_network.enums import UserActionRequired

from steam_network.protocol.protobuf_client import SteamLicense
from steam_network.protocol.consts import EFriendRelationship, EResult
from steam_network.protocol_client import ProtocolClient
from steam_network.protocol.steam_types import ProtoUserInfo


class ProtoResponse(NamedTuple):
    package_id: int


class AchievementBlock(NamedTuple):
    achievement_id: int
    unlock_time: List[int]


STEAM_ID = 71231321
MINIPROFILE_ID = 123
ACCOUNT_NAME = "john"
TOKEN = "TOKEN"


@pytest.fixture
def protobuf_client(mocker):
    mock = mocker.patch("steam_network.protocol_client.ProtobufClient")
    return mock.return_value

@pytest.fixture()
def friends_cache():
    return MagicMock()

@pytest.fixture()
def games_cache():
    return MagicMock()

@pytest.fixture()
def stats_cache():
    return MagicMock()

@pytest.fixture()
def user_info_cache():
    return AsyncMock()

@pytest.fixture()
def local_machine_cache():
    return MagicMock()

@pytest.fixture()
def times_cache():
    return MagicMock()

@pytest.fixture()
def used_server_cellid():
    return MagicMock()

@pytest.fixture()
def ownership_ticket_cache():
    return MagicMock()

@pytest.fixture()
def translations_cache():
    return dict()

@pytest.fixture
def client(protobuf_client, friends_cache, games_cache, translations_cache, stats_cache, times_cache, user_info_cache, local_machine_cache, ownership_ticket_cache, used_server_cellid):
    return ProtocolClient(protobuf_client, friends_cache, games_cache, translations_cache, stats_cache, times_cache, user_info_cache, local_machine_cache, ownership_ticket_cache, used_server_cellid)


@pytest.mark.asyncio
async def test_close(client, protobuf_client):
    protobuf_client.close.return_value = async_return_value(None)
    await client.close(True)
    protobuf_client.close.assert_called_once_with(True)


@pytest.mark.asyncio
async def test_authenticate_success(client, protobuf_client):
    protobuf_client.send_log_on_token_message.return_value = async_return_value(None)
    auth_task = asyncio.create_task(client.finalize_login(ACCOUNT_NAME, STEAM_ID, TOKEN, None))
    await skip_loop()
    await client._login_token_handler(EResult.OK, STEAM_ID, None)
    await auth_task
    protobuf_client.send_log_on_token_message.assert_called_once_with(ACCOUNT_NAME, STEAM_ID, TOKEN, ANY, ANY, ANY)


@pytest.mark.asyncio
async def test_login_token_handler_updates_cell_id(client):
    client._used_server_cell_id = 0

    await client._login_token_handler(EResult.OK, STEAM_ID, None, 42)

    assert client._used_server_cell_id == 42


@pytest.mark.asyncio
async def test_authenticate_failure(client, protobuf_client):
    auth_lost_handler = MagicMock()
    protobuf_client.send_log_on_token_message.return_value = async_return_value(None)
    auth_task = asyncio.create_task(client.finalize_login(ACCOUNT_NAME, STEAM_ID, TOKEN, auth_lost_handler))
    await skip_loop()
    await client._login_token_handler(EResult.AccessDenied, None, None)
    result = await auth_task
    assert result == UserActionRequired.InvalidAuthData


@pytest.mark.asyncio
async def test_log_out(client, protobuf_client):
    auth_lost_handler = MagicMock(return_value=async_return_value(None))
    protobuf_client.send_log_on_token_message.return_value = async_return_value(None)
    auth_task = asyncio.create_task(client.finalize_login(ACCOUNT_NAME, STEAM_ID, TOKEN, auth_lost_handler))
    await skip_loop()
    await client._login_token_handler(EResult.OK, STEAM_ID, None)
    await auth_task
    await protobuf_client.log_off_handler(EResult.Banned)
    auth_lost_handler.assert_called_once()
    error = auth_lost_handler.call_args.args[0]
    assert isinstance(error, Banned)
    assert error.args[0]["result"] == EResult.Banned


@pytest.mark.asyncio
async def test_protocol_connection_with_authentication(
    client,
    protobuf_client,
):
    protobuf_client.send_log_on_token_message.return_value = async_return_value(None)
    protobuf_client.run = AsyncMock()

    auth_task = asyncio.create_task(client.finalize_login(ACCOUNT_NAME, STEAM_ID, TOKEN, None))
    run_task = asyncio.create_task(client.run())
    await skip_loop()
    await client._login_token_handler(EResult.OK, STEAM_ID, None)
    await auth_task
    await run_task

    protobuf_client.send_log_on_token_message.assert_called_once_with(ACCOUNT_NAME, STEAM_ID, TOKEN, ANY, ANY, ANY)


@pytest.mark.asyncio
async def test_protocol_connection_failure_with_backend_not_available__eresult48(client, protobuf_client):
    protobuf_client.run.side_effect = BackendNotAvailable(str(EResult.TryAnotherCM))

    with pytest.raises(BackendNotAvailable):
        await client.run()


@pytest.mark.asyncio
async def test_relationship_initial(client, protobuf_client, friends_cache):
    friends = {
        15: EFriendRelationship.Friend,
        56: EFriendRelationship.Friend
    }

    protobuf_client.set_persona_state.return_value = async_return_value(None)
    protobuf_client.get_friends_statuses.return_value = async_return_value(None)
    protobuf_client.get_user_infos.return_value = async_return_value(None)
    await protobuf_client.relationship_handler(False, friends)
    friends_cache.reset.assert_called_once_with([15, 56])
    protobuf_client.get_friends_statuses.assert_called_once_with()
    protobuf_client.get_user_infos.assert_called_once_with([15, 56], ANY)


@pytest.mark.asyncio
async def test_relationship_update(client, protobuf_client, friends_cache):
    friends = {
        15: EFriendRelationship.Friend,
        56: EFriendRelationship.None_
    }
    protobuf_client.get_friends_statuses.return_value = async_return_value(None)
    protobuf_client.get_user_infos.return_value = async_return_value(None)
    await protobuf_client.relationship_handler(True, friends)
    friends_cache.add.assert_called_once_with(15)
    friends_cache.remove.assert_called_once_with(56)
    protobuf_client.get_friends_statuses.assert_called_once_with()
    protobuf_client.get_user_infos.assert_called_once_with([15], ANY)


@pytest.mark.asyncio
async def test_user_info(client, protobuf_client, friends_cache):
    user_id = 15
    user_info = ProtoUserInfo("Ola")
    friends_cache.update = AsyncMock()
    await protobuf_client.user_info_handler(user_id, user_info)
    friends_cache.update.assert_called_once_with(user_id, user_info)


@pytest.mark.asyncio
async def test_license_import(client):
    licenses_to_check = [SteamLicense(ProtoResponse(123), False),
                        SteamLicense(ProtoResponse(321), True)]
    client._protobuf_client.get_packages_info = AsyncMock()
    await client._license_import_handler(licenses_to_check)

    client._games_cache.reset_storing_map.assert_called_once()
    client._protobuf_client.get_packages_info.assert_called_once_with(licenses_to_check)


@pytest.mark.asyncio
async def test_merge_achievements_and_update_stats(client, stats_cache):
    # Setup mock responses for both user achievements and game achievement schema
    from steam_network.protocol.messages.steammessages_player_pb2 import (
        CPlayer_GetUserAchievements_Response,
        CPlayer_GetGameAchievements_Response,
    )
    
    game_id = "12345"
    
    # 1. Mock Game achievements response (schema)
    game_resp = CPlayer_GetGameAchievements_Response()
    ach1 = game_resp.achievements.add()
    ach1.internal_key = 1
    ach1.internal_name = "ACH_1_INTERNAL"
    ach1.localized_name = "Super achievement 1"
    
    ach2 = game_resp.achievements.add()
    ach2.internal_key = 2
    ach2.internal_name = "ACH_2_INTERNAL"
    ach2.localized_name = "Super achievement 2"

    # 2. Mock User achievements response (unlocks)
    user_resp = CPlayer_GetUserAchievements_Response()
    u_ach1 = user_resp.achievements.add()
    u_ach1.internal_key = 1
    u_ach1.unlocked = True
    u_ach1.unlock_time = 1511111111
    
    u_ach2 = user_resp.achievements.add()
    u_ach2.internal_key = 2
    u_ach2.unlocked = False
    u_ach2.unlock_time = 0

    # Execute handlers
    client._game_achievements_handler(game_id, game_resp)
    client._user_achievements_handler(game_id, user_resp)
    
    # Verify stats_cache update was called with merged/correct achievements list
    stats_cache.update_stats.assert_called_once_with(game_id, None, [
        {
            'id': 1,
            'unlock_time': 1511111111,
            'name': "Super achievement 1"
        }
    ])
