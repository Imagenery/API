from fastapi import APIRouter, Request, Response

from ...utilities import Client, limiter
from . import pillow

router = APIRouter(prefix="/image")


async def process_route(url: str, operation: str) -> Response:
    image_bytes = await Client.fetch_image(url)
    image, image_format = await pillow.process_image(image_bytes, getattr(pillow, operation))
    return Response(image.read(), media_type=f"image/{image_format}")


@router.get("/invert")
@limiter.limit("30/minute")
async def image_invert(request: Request, url: str):
    return await process_route(url, "invert")


@router.get("/deepfry")
@limiter.limit("30/minute")
async def image_deepfry(request: Request, url: str):
    return await process_route(url, "deepfry")


@router.get("/lego")
@limiter.limit("30/minute")
async def image_lego(request: Request, url: str):
    return await process_route(url, "lego")
