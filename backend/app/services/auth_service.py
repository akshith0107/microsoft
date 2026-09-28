from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException, NotFoundException
from app.core.security import get_password_hash, verify_password, create_access_token, hash_token
from app.db.models.user import User
from app.db.models.shop import Shop, ShopMember, Role
from app.db.models.auth import UserSession, PasswordResetToken, EmailVerificationToken, OTPVerification, OTPPurpose
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def signup(self, signup_data: SignupRequest) -> Tuple[User, Shop, str]:
        # Check existing user
        res = await self.db.execute(select(User).where(User.email == signup_data.email))
        if res.scalar_one_or_none():
            raise ConflictException("Email address already registered")

        if signup_data.phone:
            res_phone = await self.db.execute(select(User).where(User.phone == signup_data.phone))
            if res_phone.scalar_one_or_none():
                raise ConflictException("Phone number already registered")

        # 1. Create User
        user = User(
            name=signup_data.name,
            email=signup_data.email,
            phone=signup_data.phone,
            password_hash=get_password_hash(signup_data.password),
            preferred_language=signup_data.preferred_language,
            is_active=True,
            email_verified=False,
            phone_verified=False
        )
        self.db.add(user)
        await self.db.flush()

        # 2. Create Shop
        shop = Shop(
            name=signup_data.shop_name,
            owner_id=user.id,
            phone=signup_data.phone,
            email=signup_data.email,
            country="IN",
            currency="INR",
            timezone="Asia/Kolkata"
        )
        self.db.add(shop)
        await self.db.flush()

        # 3. Create OWNER ShopMember
        member = ShopMember(
            shop_id=shop.id,
            user_id=user.id,
            role=Role.OWNER,
            is_active=True
        )
        self.db.add(member)

        # 4. Generate Access Token
        access_token = create_access_token(
            subject=user.id,
            extra_claims={"shop_id": str(shop.id), "role": Role.OWNER.value}
        )

        await self.db.commit()
        await self.db.refresh(user)
        await self.db.refresh(shop)

        return user, shop, access_token

    async def login(self, login_data: LoginRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> TokenResponse:
        res = await self.db.execute(select(User).where(User.email == login_data.email))
        user = res.scalar_one_or_none()

        if not user or not verify_password(login_data.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("User account is disabled")

        user.last_login_at = datetime.now(timezone.utc)

        # Find user's active shop
        mem_res = await self.db.execute(
            select(ShopMember).where(
                ShopMember.user_id == user.id,
                ShopMember.is_active == True
            )
        )
        membership = mem_res.scalars().first()
        active_shop_id = membership.shop_id if membership else None

        access_token = create_access_token(
            subject=user.id,
            extra_claims={"shop_id": str(active_shop_id) if active_shop_id else None}
        )

        # Create session record
        session_token_hash = hash_token(access_token)
        session = UserSession(
            user_id=user.id,
            session_token_hash=session_token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(session)
        await self.db.commit()

        return TokenResponse(
            access_token=access_token,
            expires_in_seconds=3600 * 24,
            user_id=user.id,
            shop_id=active_shop_id
        )

    async def logout(self, user_id: UUID, token: str) -> bool:
        session_token_hash = hash_token(token)
        res = await self.db.execute(
            select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.session_token_hash == session_token_hash
            )
        )
        session = res.scalar_one_or_none()
        if session:
            session.revoked_at = datetime.now(timezone.utc)
            await self.db.commit()
        return True
