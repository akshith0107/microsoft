from typing import List
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_shop
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop
from app.db.models.expense import Expense, ExpenseCategory
from app.schemas.common import APIResponse
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseCategoryCreate

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("", response_model=APIResponse[List[ExpenseRead]])
async def list_expenses(
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    stmt = (
        select(Expense, ExpenseCategory)
        .outerjoin(ExpenseCategory, ExpenseCategory.id == Expense.category_id)
        .where(Expense.shop_id == shop.id)
        .order_by(Expense.expense_date.desc())
    )
    res = await db.execute(stmt)
    records = res.all()

    out = []
    for exp, cat in records:
        r = ExpenseRead(
            id=exp.id,
            shop_id=exp.shop_id,
            category_id=exp.category_id,
            category_name=cat.name if cat else "General",
            amount=exp.amount,
            description=exp.description,
            expense_date=exp.expense_date,
            payment_method=exp.payment_method,
            created_by=exp.created_by,
            created_at=exp.created_at
        )
        out.append(r)
    return APIResponse(data=out)


@router.post("", response_model=APIResponse[ExpenseRead])
async def create_expense(
    exp_in: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    exp = Expense(
        shop_id=shop.id,
        category_id=exp_in.category_id,
        amount=exp_in.amount,
        description=exp_in.description,
        expense_date=exp_in.expense_date or datetime.now(timezone.utc),
        payment_method=exp_in.payment_method,
        created_by=current_user.id
    )
    db.add(exp)
    await db.commit()
    await db.refresh(exp)

    return APIResponse(data=ExpenseRead.model_validate(exp), message="Expense recorded successfully")
