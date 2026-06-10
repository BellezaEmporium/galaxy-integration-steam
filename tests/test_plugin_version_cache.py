import asyncio
from unittest.mock import Mock, AsyncMock
import pytest


FIRST_SETUP_VERSION_CACHE = "auth_setup_on_version"


@pytest.mark.parametrize("initial_version", [
    "0.53",
    "1.53",
    "2.2.10",
])
def test_ensure_version_is_cached_on_pass_login_credentials(
    create_plugin_with_backend,
    register_mock_backend,
    initial_version,
    mocker,
):
    current_plugin_version = "2.2.10"
    mocker.patch("plugin.__version__", current_plugin_version)
    backend = register_mock_backend("A").return_value
    backend.pass_login_credentials = AsyncMock(return_value=Mock(name="auth result"))
    plugin = create_plugin_with_backend("A", connected_on_version=initial_version)

    asyncio.run(
        plugin.pass_login_credentials(
            Mock(str, name="step"),
            Mock(dict, name="credentials"),
            Mock(dict, name="cookies"),
        )
    )
    
    assert plugin.persistent_cache[FIRST_SETUP_VERSION_CACHE] == current_plugin_version


def test_do_not_cache_version_on_authenticate(
    create_plugin_with_backend,
    register_mock_backend,
    mocker
):
    current_plugin_version = "2.2.10"
    initial_version = "1.2.9"
    mocker.patch("plugin.__version__", current_plugin_version)
    backend = register_mock_backend("A").return_value
    backend.authenticate = AsyncMock(return_value=Mock(name="auth result"))
    plugin = create_plugin_with_backend("A", connected_on_version=initial_version)

    asyncio.run(plugin.authenticate(stored_credentials=Mock(name="stored_credentials")))
    
    assert plugin.persistent_cache[FIRST_SETUP_VERSION_CACHE] == initial_version
