import re


class Constants:
    """
    A Class that defines the constants used within the application
    """
    # Constants for CTIX Integration
    CTIX_INSTANCE_NAME = ""
    CTIX_BASE_URL = ""
    CTIX_ACCESS_ID = ""
    CTIX_SECRET_KEY = ""
    CTIX_VERIFY_CERTIFICATE = True
    CTIX_SAVED_RESULT_SET_TAG = ""
    DATA_FIELDS_EXTRACTED = ["modified_timestamp", "is_whitelisted", "created_timestamp", "TLP", "is_false_positive", "score",
                   "is_deprecated", "indicator", "indicator_type", "ctix_id"]
    CTIX_BASE_URL_SUBSTITUTION_PATTERN = re.compile(r"(\/openapi\/?$)")
    CTIX_SAVED_RESULT_SET_API_SUBSTITUTION_PATTERN = re.compile(r"(\/?ingestion\/?)")
    CTIX_API_VERSION = "v3"

    # Constants for Humio Integration
    HUMIO_BASE_URL = ""
    HUMIO_HEC_URL = "{base_url}/api/v1/ingest/hec/raw".format(base_url=HUMIO_BASE_URL)
    HUMIO_HEC_BEARER_TOKEN = ""
    HUMIO_HEC_CONTENT_TYPE = "{'Content-Type': 'application/json', 'Accept':'application/json'}"
    HUMIO_HEC_VERIFY_CERTIFICATE = True

    # Constants for this Application
    PICKLE_FILE_PATH = "checkpoints/"
    LOG_LEVEL = "debug"
    LOG_FORMAT = "%(asctime)s.%(msecs)03d :: %(levelname)s :: %(name)s :: %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    LOG_BASE_FOLDER = "logs/"
    LOG_FILE_NAME = "app.log"
    LOG_FILE_PATH = "{log_folder_path}/{log_file_name}".format(
        log_folder_path=LOG_BASE_FOLDER.rstrip("/"),
        log_file_name=LOG_FILE_NAME
    )
    LOG_MAX_FILE_SIZE = 2097152  # in Bytes
    LOG_BACKUP_COUNT = 10
    CHECKPOINTS_FILE_BASE_PATH = "checkpoints/"
    CHECKPOINTS_FILE_NAME = "checkpoints"
    CHECKPOINTS_FILE_EXTENSION = "pkl"
    CHECKPOINTS_FILE_PATH = "{base_folder_path}/{file_name}.{file_extension}".format(
        base_folder_path=CHECKPOINTS_FILE_BASE_PATH.rstrip("/"),
        file_name=CHECKPOINTS_FILE_NAME,
        file_extension=CHECKPOINTS_FILE_EXTENSION
    )