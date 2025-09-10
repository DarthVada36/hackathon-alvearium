from fastapi import APIRouter

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("/ping")
def ping():
	return {"service": "routes", "ok": True}
