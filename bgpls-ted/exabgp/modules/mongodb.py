import pymongo
from os import environ


class MongoDB:
    def __init__(self):
        self.uri = environ.get("MONGODB_URI", "mongodb://localhost:27017")
        self.client = pymongo.MongoClient(self.uri)
        self.db = None
        self.set_database()

    def set_database(self, default_database=environ.get("MONGODB_DATABASE", "bgpls")):
        self.db = self.client[default_database]

    def get_collections(self):
        return self.db.list_collection_names()

    def delete_collection(self, collection, query_filter={}):
        return self.db[collection].remove(query_filter)

    def update(self, collection, query_filter, update_query):
        return self.db[collection].update(
            query_filter, {"$set": update_query}, upsert=True
        )

    def insert_one(self, collection, data):
        collection = self.db[collection]
        record = collection.insert_one(data)
        return record.inserted_id

    def insert_many(self, collection, data):
        if not isinstance(data, list):
            return None
        collection = self.db[collection]
        records = collection.insert_many(data)
        return records.inserted_ids

    def find(
        self, collection, query_filter={}, include_fields={"_id": False}, limit=25
    ):
        if not isinstance(query_filter, dict):
            return None
        if limit:
            results = list(
                self.db[collection]
                .find(query_filter, include_fields)
                .limit(limit)
                .sort([("$natural", pymongo.DESCENDING)])
            )
        else:
            results = list(
                self.db[collection]
                .find(query_filter, include_fields)
                .sort([("$natural", pymongo.DESCENDING)])
            )

        return results

    def find_one(self, collection, query_filter, include_fields={"_id": False}):
        if not isinstance(query_filter, dict):
            return None
        return self.db[collection].find_one(query_filter, include_fields)

    def delete(self, collection, query_filter):
        if not isinstance(query_filter, dict):
            return None
        return self.db[collection.delete(query_filter)]

    def delete_one(self, collection, query_filter):
        if not isinstance(query_filter, dict):
            return None
        return self.db[collection].delete_one(query_filter)

    def remove(self, collection, query_filter={}):
        if not isinstance(query_filter, dict):
            return None
        return self.db[collection].remove(query_filter)

    def remove_from_collections(self, collections=[], query_filter={}):
        if not isinstance(query_filter, dict):
            return None
        results = []
        for collection in collections:
            results.append(self.db[collection].remove(query_filter))
        return results

    def update_one(self, collection, query_filter, update_query):
        if not isinstance(query_filter, dict) or not isinstance(update_query, dict):
            return None
        return self.db[collection].update_one(query_filter, update_query)

    def close(self):
        if not self.client:
            return True
        self.client.close()
        return True
