from fastapi import APIRouter

router = APIRouter(prefix="/family", tags=["family"])


@router.get("/ping")
def ping():
	return {"service": "family", "ok": True}
