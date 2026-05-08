from config import db
from datetime import datetime

class Promotion:
    """Model Khuyến mãi (Promotion)"""
    def __init__(self, code, value, type="PERCENT", active=True, expires_at=None):
        self.code = code.upper()
        self.value = float(value)
        self.type = type
        self.active = bool(active)
        self.expires_at = expires_at
        self._id = None

    def save(self):
        res = db.promotions.insert_one({
            "code": self.code,
            "type": self.type,
            "value": self.value,
            "active": self.active,
            "expires_at": self.expires_at
        })
        self._id = res.inserted_id
        return self._id

    @staticmethod
    def find_by_code(code):
        return db.promotions.find_one({"code": code.upper()})

    @staticmethod
    def apply(code, amount):
        promo = Promotion.find_by_code(code)
        amount = float(amount)
        if not promo or not promo.get("active", False):
            return {"valid": False, "amount": amount, "discount": 0.0, "final": amount}

        exp = promo.get("expires_at")
        if exp:
            try:
                if datetime.fromisoformat(exp) < datetime.utcnow():
                    return {"valid": False, "amount": amount, "discount": 0.0, "final": amount}
            except Exception:
                pass

        if promo["type"] == "PERCENT":
            discount = amount * (promo["value"] / 100.0)
        else:
            discount = promo["value"]

        final = max(0.0, amount - discount)
        return {"valid": True, "amount": amount, "discount": round(discount, 2), "final": round(final, 2), "promotion": {"code": promo["code"], "type": promo["type"], "value": promo["value"]}}
