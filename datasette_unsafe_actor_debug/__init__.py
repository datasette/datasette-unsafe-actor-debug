from datasette import hookimpl, Response
import json


def is_enabled(datasette):
    plugin_config = datasette.plugin_config("datasette-unsafe-actor-debug") or {}
    return plugin_config.get("enabled", False)


async def unsafe_actor(datasette, request):
    error = ""

    actor_from_get = request.args.get("actor")

    if request.method == "POST":
        data = await request.post_vars()
        actor_raw = data.get("actor")

        try:
            actor = json.loads(actor_raw)
            response = Response.redirect("/")
            response.set_cookie(
                "ds_actor",
                datasette.sign({"a": actor}, "actor"),
            )
            return response
        except json.JSONDecodeError:
            error = "Invalid JSON"

    return Response.html(
        await datasette.render_template(
            "unsafe_actor.html",
            {
                "error": error,
                "actor_from_get": actor_from_get,
            },
            request=request,
        )
    )


@hookimpl
def register_routes(datasette):
    if is_enabled(datasette):
        return [
            (r"^/-/unsafe-actor$", unsafe_actor),
        ]
