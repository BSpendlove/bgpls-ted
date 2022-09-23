from typing import Any
from os import environ

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient

from app.dependencies import get_db

app = FastAPI(title="bgpls-ted")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def bgpls_topology(
    request: Request, db: AsyncIOMotorClient = Depends(get_db)
) -> Any:
    topology = {"nodes": []}
    total_nodes = 0
    total_links = 0
    total_prefixes_v4 = 0
    total_prefixes_v6 = 0

    async for node in db[environ.get("BGPLS_COLLECTION_NODES","bgpls_nodes")].find(
        {"node_descriptors.autonomous_system": environ.get("BGPLS_DEFAULT_ASN", 65531)}, {"_id": False}
    ):
        total_nodes += 1

        node_id = node["node_id"]
        node_links = []
        node_prefixes_v4 = []
        node_prefixes_v6 = []

        async for link in db[environ.get("BGPLS_COLLECTION_LINKS","bgpls_links")].find(
            {"node_id": node_id}, {"_id": False}
        ):
            total_links += 1
            node_links.append(link)

        async for prefix_v4 in db[environ.get("BGPLS_COLLECTION_PREFIXES_V4","bgpls_prefixes_v4")].find(
            {"node_id": node_id}, {"_id": False}
        ):
            total_prefixes_v4 += 1
            node_prefixes_v4.append(prefix_v4)

        async for prefix_v6 in db[environ.get("BGPLS_COLLECTION_PREFIXES_V6","bgpls_prefixes_v6")].find(
            {"node_id": node_id}, {"_id": False}
        ):
            total_prefixes_v6 += 1
            node_prefixes_v6.append(prefix_v6)

        node.update(
            {
                "links": node_links,
                "prefixes_v4": node_prefixes_v4,
                "prefixes_v6": node_prefixes_v6,
            }
        )
        topology["nodes"].append(node)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "topology": topology,
            "bgpls_nodes": total_nodes,
            "bgpls_links": total_links,
            "bgpls_prefixes_v4": total_prefixes_v4,
            "bgpls_prefixes_v6": total_prefixes_v6,
        },
    )


@app.get("/links", response_class=HTMLResponse)
async def bgpls_topology_links(
    request: Request, node_id: str, db: AsyncIOMotorClient = Depends(get_db)
) -> Any:
    node_name = await db[environ.get("BGPLS_COLLECTION_NODES","bgpls_nodes")].find_one(
        {"node_id": node_id},
        {"attributes": {"bgp_ls": {"node_name": True}}, "_id": False},
    )

    if node_name:
        node_name = node_name["attributes"]["bgp_ls"]["node_name"]

    links = (
        await db["bgpls_links"]
        .find({"node_id": node_id}, {"_id": False})
        .to_list(None)
    )
    return templates.TemplateResponse(
        "links.html",
        {
            "request": request,
            "links": links,
            "node_id": node_id,
            "node_name": node_name,
        },
    )


@app.get("/prefixes", response_class=HTMLResponse)
async def bgpls_topology_prefixes(
    request: Request, node_id: str, db: AsyncIOMotorClient = Depends(get_db)
) -> Any:

    node_name = await db[environ.get("BGPLS_COLLECTION_NODES","bgpls_nodes")].find_one(
        {"node_id": node_id},
        {"attributes": {"bgp_ls": {"node_name": True}}, "_id": False},
    )

    if node_name:
        node_name = node_name["attributes"]["bgp_ls"]["node_name"]

    prefixes_v4 = (
        await db[environ.get("BGPLS_COLLECTION_PREFIXES_V4","bgpls_prefixes_v4")]
        .find({"node_id": node_id}, {"_id": False})
        .to_list(None)
    )

    prefixes_v6 = (
        await db[environ.get("BGPLS_COLLECTION_PREFIXES_V6","bgpls_prefixes_v6")]
        .find({"node_id": node_id}, {"_id": False})
        .to_list(None)
    )

    return templates.TemplateResponse(
        "prefixes.html",
        {
            "request": request,
            "prefixes_v4": prefixes_v4,
            "prefixes_v6": prefixes_v6,
            "node_id": node_id,
            "node_name": node_name,
        },
    )


@app.get("/links/from_neighbor", response_class=HTMLResponse)
async def bgpls_topology_links_by_neighbor_address(
    request: Request, neighbor_address: str, db: AsyncIOMotorClient = Depends(get_db)
) -> Any:

    remote_link = await db[environ.get("BGPLS_COLLECTION_LINKS","bgpls_links")].find_one(
        {"interface_address": {"interface_address": neighbor_address}}, {"_id": False}
    )

    node_id = remote_link["node_id"]
    node_name = await db[environ.get("BGPLS_COLLECTION_NODES","bgpls_nodes")].find_one(
        {"node_id": node_id},
        {"attributes": {"bgp_ls": {"node_name": True}}, "_id": False},
    )

    if node_name:
        node_name = node_name["attributes"]["bgp_ls"]["node_name"]

    links = (
        await db[environ.get("BGPLS_COLLECTION_LINKS","bgpls_links")]
        .find({"node_id": node_id}, {"_id": False})
        .to_list(None)
    )
    return templates.TemplateResponse(
        "links.html",
        {
            "request": request,
            "links": links,
            "node_id": node_id,
            "node_name": node_name,
        },
    )
