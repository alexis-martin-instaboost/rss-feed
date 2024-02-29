from helpers.logger_setup import setup_logger

logger = setup_logger()
store = {}  # Global store variable

class KeyValueStore:
    def set(self, key, value):
        global store
        logger.info(f"Setting key: {key}, value: {value}")
        store[key] = value

    def get(self, key):
        global store
        logger.info(f"Getting key: {key}")
        result = store.get(key, None)
        logger.info(f"Getting key: {result}")
        return result

    def delete(self, key):
        global store
        if key in store:
            del store[key]
            logger.info(f"Key '{key}' deleted.")
        else:
            logger.info(f"Key '{key}' not found.")

    def display(self):
        global store
        logger.info("Key-Value Store:")
        for key, value in store.items():
            logger.info(f"{key}: {value}")
