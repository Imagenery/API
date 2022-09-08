from fastapi import APIRouter, Request, Response

from ...utilities import Client
from . import pillow

router = APIRouter(prefix="/image")


async def process_route(url: str, operation: str) -> Response:
    image_bytes = await Client.fetch_image(url)
    image, image_format = await pillow.process_image(image_bytes, getattr(pillow, operation))
    return Response(image.read(), media_type=f"image/{image_format}")


@router.get("/invert")
async def image_invert(request: Request, url: str):
    return await process_route(url, "invert")


@router.get("/deepfry")
async def image_deepfry(url: str):
    return await process_route(url, "deepfry")


@router.get("/lego")
async def image_lego(url: str):
    return await process_route(url, "lego")
