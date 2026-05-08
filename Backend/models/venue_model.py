from config.config import db
from bson.objectid import ObjectId

class VenueModel:
    collection = db.venues

    @staticmethod
    def get_all():
        venues = list(VenueModel.collection.find({}))
        # Convert ObjectId -> string
        for v in venues:
            v["_id"] = str(v["_id"])
        return venues

    @staticmethod
    def get_by_id(venue_id):
        try:
            venue = VenueModel.collection.find_one({"_id": ObjectId(venue_id)})
            if venue:
                venue["_id"] = str(venue["_id"])
            return venue
        except:
            return None

    @staticmethod
    def create(data):
        """Thêm venue mới"""
        result = VenueModel.collection.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def update(venue_id, data):
        """Cập nhật venue"""
        return VenueModel.collection.update_one(
            {"_id": ObjectId(venue_id)},
            {"$set": data}
        )

    @staticmethod
    def delete(venue_id):
        """Xóa venue"""
        return VenueModel.collection.delete_one({"_id": ObjectId(venue_id)})
from config.config import db
from bson.objectid import ObjectId

class VenueModel:
    collection = db.venues

    @staticmethod
    def get_all():
        venues = list(VenueModel.collection.find({}))
        # Convert ObjectId -> string
        for v in venues:
            v["_id"] = str(v["_id"])
        return venues

    @staticmethod
    def get_by_id(venue_id):
        try:
            venue = VenueModel.collection.find_one({"_id": ObjectId(venue_id)})
            if venue:
                venue["_id"] = str(venue["_id"])
            return venue
        except:
            return None

    @staticmethod
    def create(data):
        """Thêm venue mới"""
        result = VenueModel.collection.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def update(venue_id, data):
        """Cập nhật venue"""
        return VenueModel.collection.update_one(
            {"_id": ObjectId(venue_id)},
            {"$set": data}
        )

    @staticmethod
    def delete(venue_id):
        """Xóa venue"""
        return VenueModel.collection.delete_one({"_id": ObjectId(venue_id)})
