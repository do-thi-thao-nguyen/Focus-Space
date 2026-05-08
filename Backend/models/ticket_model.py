# models/ticket_model.py
from config.config import db

class TicketModel:
    collection = db.tickets

    @staticmethod
    def create_ticket(data):
        res = TicketModel.collection.insert_one(data)
        return str(res.inserted_id)

    @staticmethod
    def get_all():
        return list(TicketModel.collection.find({}))

    @staticmethod
    def get_ticket(ticket_id):
        return TicketModel.collection.find_one({"_id": ticket_id})

    @staticmethod
    def update_ticket(ticket_id, data):
        TicketModel.collection.update_one({"_id": ticket_id}, {"$set": data})

    @staticmethod
    def delete_ticket(ticket_id):
        TicketModel.collection.delete_one({"_id": ticket_id})
