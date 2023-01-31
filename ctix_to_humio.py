import time
from config.logger import get_logger
from config import helper

logger = get_logger(__name__)

if __name__ == "__main__":
    start = time.time()
    try:
        indicators = helper.fetch_data_from_ctix()
        helper.push_to_humio(indicators)
    except Exception as e:
        logger.exception(e)

    finally:
        print("-" * 50)
        print("Total Time Taken: {}s".format(time.time() - start))
