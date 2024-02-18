from datasette_test import Datasette
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("enabled", (True, False))
async def test_unsafe_actor_debug(enabled):
    datasette = Datasette(
        plugin_config={
            "datasette-unsafe-actor-debug": {
                "enabled": enabled,
            }
        }
    )
    response = await datasette.client.get("/-/unsafe-actor")
    if not enabled:
        assert response.status_code == 404
        return
    assert response.status_code == 200
    cookies = response.cookies
    assert "ds_csrftoken" in cookies
    invalid_post_response = await datasette.client.post(
        "/-/unsafe-actor",
        data={"actor": "invalid json"},
    )
    assert invalid_post_response.status_code == 200
    assert "Invalid JSON" in invalid_post_response.text
    valid_post_response = await datasette.client.post(
        "/-/unsafe-actor", data={"actor": '{"id": "hello"}'}
    )
    assert valid_post_response.status_code == 302
    assert valid_post_response.headers["Location"] == "/"
    assert "ds_actor" in valid_post_response.cookies
    ds_actor = valid_post_response.cookies["ds_actor"]
    assert datasette.unsign(ds_actor, "actor") == {"a": {"id": "hello"}}
