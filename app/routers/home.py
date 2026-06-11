from fastapi import APIRouter, Depends, Request

from app.deps import get_current_user, render

router = APIRouter(tags=["home"])


@router.get("/")
def home_page(request: Request, user=Depends(get_current_user)):
    return render(request, "home.html", user=user)
