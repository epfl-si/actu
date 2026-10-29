from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from news.models import News

from .forms import MultipleImageUploadForm, NewsImageForm
from .models import ImageRenderingError, NewsImage
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


def serve_news_image(request, image_id, resolution):
    """Serve a rendered variant of a news image as a cached JPEG.

    The rendering itself (decode, crop, resize, encoding) lives on
    NewsImage.render; this view is only the HTTP pass-through.
    """
    news_image = get_object_or_404(NewsImage, pk=image_id)

    try:
        content = news_image.render(resolution)
    except ImageRenderingError:
        raise Http404(_("Image file not found."))

    response = HttpResponse(content, content_type="image/jpeg")
    response["Cache-Control"] = "max-age=900, public"
    return response
