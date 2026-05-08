from config.config import db

class TransactionsHistoryModel:
    collection = db["transactions"]

    @staticmethod
    def get_simple_history(date=None):
        """
        Lấy lịch sử chỉ gồm 3 trường: item, date, session
        Nếu có tham số date thì lọc theo ngày
        """
        query = {}
        if date:
            query["date"] = date  # lọc theo ngày (YYYY-MM-DD)

        data = TransactionsHistoryModel.collection.find(
            query,
            {"_id": 0, "item": 1, "date": 1, "session": 1}
        )
        return list(data)
