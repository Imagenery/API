import asyncio
import functools
from io import BytesIO
from typing import Callable, Concatenate, Tuple

from PIL import Image, ImageEnhance, ImageOps, UnidentifiedImageError
from typing_extensions import Concatenate, ParamSpec

from ...errors import APIException

P = ParamSpec("P")

# Constants
LEGO: Image.Image = Image.open("./src/assets/image/lego.png").resize((32, 32), Image.ANTIALIAS)

# Utility Functions


def convert_to_pil_image(image: bytes, gif: bool = False) -> Image.Image:
    formats = ["PNG", "JPEG", "GIF"] if gif else ["PNG", "JPEG"]

    if image.__sizeof__() > 15 * (2**20):
        raise APIException(detail="Payload Exceeds Limit Of 15 MB", status_code=413)
    try:
        buffer = BytesIO(image)
        buffer.seek(0)
        return Image.open(buffer, formats=formats)
    except UnidentifiedImageError:
        raise APIException(
            detail=f"Unsupported Image Format, Supported Image Formats are {', '.join(formats)}",
            status_code=415,
        )


def convert_pil_image_to_bytesio(image: Image.Image) -> BytesIO:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    image.close()

    return buffer


def manipulate_image(
    image: bytes,
    function: Callable[Concatenate[Image.Image, P], Image.Image],
    *args,
    **kwargs,
) -> Tuple[BytesIO, str]:
    manipulated_image = convert_to_pil_image(image)
    manipulated_image = function(manipulated_image, *args, **kwargs)  # type: ignore
    return convert_pil_image_to_bytesio(manipulated_image), (manipulated_image.format or "PNG")


async def process_image(
    image: bytes,
    function: Callable[Concatenate[Image.Image, P], Image.Image],
    *args,
    **kwargs,
) -> Tuple[BytesIO, str]:
    loop = asyncio.get_event_loop()
    func = functools.partial(manipulate_image, image, function, *args, **kwargs)
    result = await loop.run_in_executor(None, func)

    return result


# Actual Manipulation Functions


def invert(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    r, g, b, a = image.split()
    rgb_image = Image.merge("RGB", (r, g, b))

    inverted_image = ImageOps.invert(rgb_image)

    r2, g2, b2 = inverted_image.split()

    return Image.merge("RGBA", (r2, g2, b2, a))


def deepfry(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    width, height = image.width, image.height
    image = image.resize((int(width**0.75), int(height**0.75)), resample=Image.LANCZOS)
    image = image.resize((int(width**0.88), int(height**0.88)), resample=Image.BILINEAR)
    image = image.resize((int(width**0.9), int(height**0.9)), resample=Image.BICUBIC)
    image = image.resize((width, height), resample=Image.BICUBIC)
    image = ImageOps.posterize(image, 4)

    r = image.split()[0]
    r = ImageEnhance.Contrast(r).enhance(2.0)
    r = ImageEnhance.Brightness(r).enhance(1.5)

    r = ImageOps.colorize(r, (254, 0, 2), (255, 255, 15))  # type: ignore

    image = Image.blend(image, r, 0.75)
    r.close()

    image = ImageEnhance.Sharpness(image).enhance(100.0)

    return image


def lego(image: Image.Image) -> Image.Image:
    def _overlay_effect(color: int, overlay: int):
        if color < 33:
            return overlay - 100
        elif color > 233:
            return overlay + 100
        else:
            return overlay - 133 + color

    def _get_new_size(base_image: Image.Image, brick_image: Image.Image, size: int | None = None):
        new_size = base_image.size
        if size:
            scale_x, scale_y = size, size
        else:
            scale_x, scale_y = brick_image.size

        if new_size[0] > scale_x or new_size[1] > scale_y:
            if new_size[0] < new_size[1]:
                scale = new_size[1] / scale_y
            else:
                scale = new_size[0] / scale_x

            new_size = (
                int(round(new_size[0] / scale)) or 1,
                int(round(new_size[1] / scale)) or 1,
            )

        return new_size

    image = image.convert("RGBA")

    # Calculate the required size of base image and set it
    image = image.resize(_get_new_size(image, LEGO, 32), Image.BILINEAR)

    base_width, base_height = image.size
    brick_width, brick_height = LEGO.size

    # The actual output image
    with Image.new("RGBA", (base_width * brick_width, base_height * brick_height), (0, 0, 0, 0)) as lego_image:
        # loop through each pixel
        for brick_x in range(base_width):
            for brick_y in range(base_height):

                # Don't apply the lego effect on a transparent pixel
                color = image.getpixel((brick_x, brick_y))
                if color[-1] == 0:
                    continue

                overlay_red, overlay_green, overlay_blue, overlay_alpha = color
                channels = LEGO.split()

                with channels[0].point(lambda color: _overlay_effect(color, overlay_red)) as r:
                    channels[0].paste(r)

                with channels[1].point(lambda color: _overlay_effect(color, overlay_green)) as g:
                    channels[1].paste(g)

                with channels[2].point(lambda color: _overlay_effect(color, overlay_blue)) as b:
                    channels[2].paste(b)

                with channels[3].point(lambda color: overlay_alpha) as a:
                    channels[3].paste(a)

                with Image.merge("RGBA", channels) as paste_image:
                    lego_image.paste(paste_image, (brick_x * brick_width, brick_y * brick_height))

        image.close()
        return lego_image
