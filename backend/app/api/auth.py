from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop, ShopMember
from app.schemas.common import APIResponse
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.user import UserRead
from app.schemas.shop import ShopRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=APIResponse[TokenResponse])
async def signup(
    signup_data: SignupRequest,
    db: AsyncSession = Depends(get_async_db)
):
    auth_service = AuthService(db)
    user, shop, access_token = await auth_service.signup(signup_data)
    token_resp = TokenResponse(
        access_token=access_token,
        expires_in_seconds=3600 * 24,
        user_id=user.id,
        shop_id=shop.id
    )
    return APIResponse(data=token_resp, message="Signup successful")


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    auth_service = AuthService(db)
    token_resp = await auth_service.login(
        login_data,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    return APIResponse(data=token_resp, message="Login successful")


@router.post("/logout", response_model=APIResponse[bool])
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    token = request.headers.get("authorization", "").replace("Bearer ", "").strip()
    auth_service = AuthService(db)
    await auth_service.logout(current_user.id, token)
    return APIResponse(data=True, message="Logged out successfully")


@router.get("/me", response_model=APIResponse[UserRead])
async def get_me(current_user: User = Depends(get_current_user)):
    return APIResponse(data=UserRead.model_validate(current_user))


@router.get("/shops", response_model=APIResponse[List[ShopRead]])
async def get_my_shops(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(Shop)
        .join(ShopMember, ShopMember.shop_id == Shop.id)
        .where(
            ShopMember.user_id == current_user.id,
            ShopMember.is_active == True
        )
    )
    shops = list(res.scalars().all())
    return APIResponse(data=[ShopRead.model_validate(s) for s in shops])
