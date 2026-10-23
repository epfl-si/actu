from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from PIL import Image

from news.models import News

from .forms import MultipleImageUploadForm, NewsImageForm
from .models import NewsImage
from .serializers import NewsImageSerializer


def _form_errors(form):
    """Flatten form errors into a list of user-facing strings."""
    return [
        str(message) for errors in form.errors.values() for message in errors
    ]


@login_required
@require_POST
def upload_news_images(request, news_id):
    """Upload one or more images for a news item."""
    news = get_object_or_404(News, pk=news_id)
    form = MultipleImageUploadForm(request.POST, request.FILES)

    if not form.is_valid():
        return JsonResponse(
            {"success": False, "images": [], "errors": _form_errors(form)},
            status=400,
        )

    with transaction.atomic():
        images = [
            NewsImageSerializer(
                NewsImage.objects.create(
                    news=news,
                    image=image,
                    created_by=request.user,
                )
            ).data
            for image in form.cleaned_data["images"]
        ]

    return JsonResponse({"success": True, "images": images, "errors": []})


@login_required
@require_POST
def edit_news_image(request, news_id, image_id):
    """Edit the metadata of a news image."""
    news_image = get_object_or_404(NewsImage, pk=image_id, news_id=news_id)
    form = NewsImageForm(request.POST, instance=news_image)

    if not form.is_valid():
        return JsonResponse(
            {"success": False, "image": None, "errors": _form_errors(form)},
            status=400,
        )

    form.save()

    return JsonResponse(
        {
            "success": True,
            "image": NewsImageSerializer(news_image).data,
            "errors": [],
        }
    )


@login_required
@require_POST
def delete_news_image(request, news_id, image_id):
    """Delete a news image and its file."""
    news_image = get_object_or_404(NewsImage, pk=image_id, news_id=news_id)
    news_image.delete()

    return JsonResponse({"success": True})


def _flatten_on_white(image):
    """Convert an image to RGB, compositing transparency on white."""
    if image.mode not in ("RGB", "RGBA", "LA", "P"):
        image = image.convert("RGB")
    if image.mode == "RGB":
        return image

    background = Image.new("RGB", image.size, (255, 255, 255))
    rgba = image.convert("RGBA")
    background.paste(rgba, mask=rgba.split()[-1])
    return background


def serve_news_image(request, image_id, resolution):
    """Serve a news image, cropped and resized, as a cached JPEG.

    "original" serves the unmodified image. "WxH" applies the stored crop
    (when set) and fits the result within the WxH box, never upscaling.
    """
    news_image = get_object_or_404(NewsImage, pk=image_id)

    try:
        image_file = news_image.image.open("rb")
        try:
            image = Image.open(image_file)
            image.load()
        finally:
            image_file.close()
    except (OSError, ValueError):
        raise Http404(_("Image file not found."))

    if resolution != "original" and all(
        getattr(news_image, f"crop_{part}") is not None
        for part in ("left", "upper", "right", "lower")
    ):
        image = image.crop(
            (
                news_image.crop_left,
                news_image.crop_upper,
                news_image.crop_right,
                news_image.crop_lower,
            )
        )

    if resolution != "original":
        width, height = (int(part) for part in resolution.split("x"))
        image.thumbnail((width, height), Image.LANCZOS)

    image = _flatten_on_white(image)

    response = HttpResponse(content_type="image/jpeg")
    response["Cache-Control"] = "max-age=900, public"
    image.save(response, "jpeg", optimize=True, quality=90, progressive=True)
    return response
