from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/ping")
def ping():
	return {"service": "chat", "ok": True}
