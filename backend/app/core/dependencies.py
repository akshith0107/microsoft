from typing import Optional, List, Callable
from uuid import UUID
from fastapi import Depends, Header, Query, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException, ForbiddenException, NotFoundException
from app.core.security import decode_access_token
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop, ShopMember, Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    if not token:
        raise UnauthorizedException("Not authenticated")

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedException("Invalid or expired authentication token")

    user_id_str = payload["sub"]
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedException("User account is inactive or not found")

    return user


async def get_current_shop(
    request: Request,
    x_shop_id: Optional[str] = Header(None, alias="X-Shop-Id"),
    shop_id_query: Optional[str] = Query(None, alias="shop_id"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Shop:
    target_shop_id_str = x_shop_id or shop_id_query
    
    # Check path parameters if present
    path_params = request.path_params
    if not target_shop_id_str and "shop_id" in path_params:
        target_shop_id_str = str(path_params["shop_id"])
    elif not target_shop_id_str and "id" in path_params and "/shops/" in request.url.path:
        target_shop_id_str = str(path_params["id"])

    if not target_shop_id_str:
        # Default to first active shop user belongs to
        stmt = select(ShopMember).where(
            ShopMember.user_id == current_user.id,
            ShopMember.is_active == True
        )
        membership_res = await db.execute(stmt)
        membership = membership_res.scalars().first()
        if not membership:
            raise NotFoundException("User does not belong to any active shop")
        target_shop_id = membership.shop_id
    else:
        try:
            target_shop_id = UUID(target_shop_id_str)
        except ValueError:
            raise ForbiddenException("Invalid Shop ID format")

    # Validate user active membership in target shop
    stmt = select(ShopMember).where(
        ShopMember.shop_id == target_shop_id,
        ShopMember.user_id == current_user.id,
        ShopMember.is_active == True
    )
    membership_res = await db.execute(stmt)
    membership = membership_res.scalar_one_or_none()

    if not membership:
        raise ForbiddenException("Access denied to requested shop")

    shop_res = await db.execute(select(Shop).where(Shop.id == target_shop_id))
    shop = shop_res.scalar_one_or_none()
    if not shop:
        raise NotFoundException("Shop not found")

    # Attach current role to shop for easy downstream access
    setattr(shop, "current_user_role", membership.role)

    return shop


def require_role(allowed_roles: List[Role]) -> Callable:
    async def role_checker(
        shop: Shop = Depends(get_current_shop)
    ) -> Shop:
        current_role = getattr(shop, "current_user_role", None)
        if not current_role or current_role not in allowed_roles:
            raise ForbiddenException(f"Role level {allowed_roles} required for this action")
        return shop
    return role_checker
