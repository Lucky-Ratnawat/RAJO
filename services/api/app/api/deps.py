from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db


def get_admin_db(db: Session = Depends(get_db)) -> Session:
    # Placeholder until auth/roles are wired in.
    # Keeping the dependency separate makes it easy to enforce admin access later.
    return db


def get_object_or_404(instance: object | None, detail: str) -> object:
    if instance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return instance
