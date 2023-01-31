import hmac
import hashlib
import base64
import json
import requests
import time
import os
import pickle
from .logger import get_logger
from .constants import Constants as constants

logger = get_logger(__name__)


def do_sanity_check(check_checkpoints_file_folder=True):
    logger.debug("Executing function: {}()".format(do_sanity_check.__name__))
    if check_checkpoints_file_folder:
        ensure_directory_exists(constants.CHECKPOINTS_FILE_PATH)


def ensure_directory_exists(file_path):
    logger.debug("Executing function: {}()".format(
        ensure_directory_exists.__name__))

    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        logger.info("Creating Directory: {}".format(directory))
        os.makedirs(directory)
    else:
        logger.info("Found Directory: {}".format(directory))


def generate_signature(expires, access_id, secret_key):
    logger.debug("Executing function: {}()".format(
        generate_signature.__name__))
    to_sign = '{}\n{}'.format(access_id, expires)
    signature = base64.b64encode(
        hmac.new(
            secret_key.encode('utf-8'),
            to_sign.encode('utf-8'),
            hashlib.sha1
        ).digest()
    ).decode("utf-8")
    return signature


def store_data_as_pickle(data={}, file_path=None):
    logger.debug("Executing function: {}()".format(store_data_as_pickle.__name__))
    success = False
    if not file_path:
        logger.exception(
            "Pickle File Path can not be Empty, the pickle file creation will be skipped.")

    else:

        try:
            with open(file_path, "wb") as f:
                pickle.dump(data, f)
            success = True
        except IOError as e:
            # Assuming file does not exist
            logger.exception('Caught and exception while trying to write to File "{}" :\n{}'.format(
                file_path, e))
        except Exception as e:
            logger.exception('Caught and exception while trying to write to File "{}" :\n{}'.format(
                file_path, e))

    return success


def load_pickled_data(file_path=None):
    logger.debug("Executing function: {}()".format(load_pickled_data.__name__))

    extracted_data = {}

    if not file_path:
        logger.error(
            "Pickle File Path can not be Empty, the file read operation will be skipped.")

    elif not os.path.exists(file_path):
        logger.error(
            "File {} does not exist and therefore can read".format(file_path))
    else:

        try:
            with open(file_path, "rb") as f:
                extracted_data = pickle.load(f)
        except IOError as e:
            logger.exception('Caught and exception while trying to read File "{}" :\n{}'.format(
                file_path, e))
        except Exception as e:
            logger.exception('Caught and exception while trying to read File "{}" :\n{}'.format(
                file_path, e))

    return extracted_data


def save_check_point(key, value):
    logger.debug("Executing function: {}()".format(
        save_check_point.__name__))
    success = True
    try:
        checkpoints = load_pickled_data(constants.CHECKPOINTS_FILE_PATH)
    except Exception as e:
        checkpoints = {}
        logger.error(
            f"Fatal Error: Unable to load checkpoints file at: {constants.CHECKPOINTS_FILE_PATH}.\
                    Checkpoint would be reset.\nException Encountered: {e}")

    try:
        checkpoints.update({
            key: value
        })

        success = store_data_as_pickle(data=checkpoints, file_path=constants.CHECKPOINTS_FILE_PATH)

    except Exception as e:
        logger.error(
            f"Fatal Error: Unable to save checkpoints to file: {constants.CHECKPOINTS_FILE_PATH}. Checkpoint could not be saved.\nException Encountered: {e}")
    else:
        if not isinstance(checkpoints, dict) or not success:
            logger.error(
                f"Fatal Error: Unable to save checkpoints to file: {constants.CHECKPOINTS_FILE_PATH}.Checkpoint could not be saved.")


def get_check_point(key):
    logger.debug("Executing function: {}()".format(
        get_check_point.__name__))

    try:
        checkpoints = load_pickled_data(constants.CHECKPOINTS_FILE_PATH)
    except Exception as e:
        logger.error(
            f"Fatal Error: Unable to load checkpoints file at: {constants.CHECKPOINTS_FILE_PATH}. All the "
            f"checkpoints will be reset.\nException Encountered: {e}")
        checkpoints = {}

    else:
        if not isinstance(checkpoints, dict):
            logger.error(
                f"Fatal Error: Unable to read checkpoints file at: {constants.CHECKPOINTS_FILE_PATH}. All the "
                f"checkpoints will be reset.")
            checkpoints = {}
    return checkpoints.get(key, None)


def push_to_humio(event_data):
    success = True
    logger.debug("Executing function: {}()".format(
        push_to_humio.__name__))

    logger.info(f'Starting the data push to Humio HEC')

    try:

        # Prepare the data for humio ingestion
        formatted_data = "\n".join(map(str, event_data))
        formatted_data = formatted_data.replace("'", '"')
        formatted_data = json.dumps(formatted_data)
        formatted_data = json.loads(formatted_data)
        formatted_data = formatted_data.replace("True", 'true')
        formatted_data = formatted_data.replace("False", 'false')
        formatted_data = formatted_data.replace("None", 'null')

        # Prepare request parameters
        header = {
            "Authorization": "Bearer " + constants.HUMIO_HEC_BEARER_TOKEN,
            "Content-Type": constants.HUMIO_HEC_CONTENT_TYPE
        }
        r = requests.post(url=constants.HUMIO_HEC_URL, headers=header, data=formatted_data.encode(
            'utf-8'), verify=constants.HUMIO_HEC_VERIFY_CERTIFICATE, timeout=300)
        transmit_result = r.status_code
        logger.info(f'Transmission status code for data push to HEC: {transmit_result}')
        logger.info(f'Transmission results for data push to HEC: {r.json()}')

    except requests.exceptions.RequestException as e:
        logger.info(f'HEC: Unable to evaluate and transmit sensor_data event: Error: {e}')
        try:
            logger.error('HEC: This is fatal error, please review and correct the issue - CTIX Indicators to Humio is '
                         'shutting down')
            success = False
        except:
            success = False

    finally:
        return success


def fetch_data_from_ctix():
    logger.debug("Executing function: {}()".format(
        fetch_data_from_ctix.__name__))

    do_sanity_check(check_checkpoints_file_folder=True)

    # generate request expiry time
    expires = int(time.time() + 20)

    if str(constants.CTIX_BASE_URL).startswith("http://"):
        logger.error("Insecure Connection is not allowed. Base URL must use HTTPS Protocol for secure connections")
        raise ValueError("Insecure Connection is not allowed. Base URL must use HTTPS Protocol for secure connections")
        return

    # generate signature
    try:
        signature = generate_signature(expires, constants.CTIX_ACCESS_ID, constants.CTIX_SECRET_KEY)
    except Exception as e:
        logger.error("Fatal Error: Caught an exception while generating Authentication Signature: {}".format(e))
        return
    else:
        logger.debug("Authentication Signature Generated Successfully")

    # get last run date
    last_run_date = get_check_point("last_run_date_{}".format(constants.CTIX_INSTANCE_NAME))
    if not last_run_date:
        last_run_date = 0

    logger.debug("Last Successful Run Date: {}".format(last_run_date))

    # get last page number
    page_number = get_check_point("page_number_{}".format(constants.CTIX_INSTANCE_NAME))
    # page number is set to 0 if the last poll was successful in fetching data
    # from all pages
    if not page_number:
        page_number = 1
        logger.debug("Starting Polling from Page: {}".format(page_number))
    else:
        logger.debug("Resuming Polling from Page: {}".format(page_number))

    # Prepare request parameters
    url = "{}/{}".format(constants.CTIX_BASE_URL.rstrip("/"), "ingestion/rules/save_result_set/")
    params = {
        "version": constants.CTIX_API_VERSION,
        "AccessID": constants.CTIX_ACCESS_ID,
        "Expires": expires,
        "Signature": signature,
        "page_size": 100,
        "from_timestamp": last_run_date,
        "page": page_number
    }
    if constants.CTIX_SAVED_RESULT_SET_TAG:
        if constants.CTIX_SAVED_RESULT_SET_TAG.strip():
            params["label_name"] = constants.CTIX_SAVED_RESULT_SET_TAG.strip()

    logger.debug("Polling Endpoint: {}".format(url))

    # handle paginated results
    next_page = url
    ioc_data_set = []  # Hold raw results from each successful API Request
    next_page_base_url = constants.CTIX_BASE_URL_SUBSTITUTION_PATTERN.sub("", constants.CTIX_BASE_URL.rstrip("/"))

    # Use these variables in While loop to break after certain iterations
    iteration_threshold = 10
    count = 0

    # set current_page_number for iteration
    if page_number:
        current_page_number = page_number
    else:
        current_page_number = 1

    try:
        # Loop through the results until last page is reached,
        # i.e. when "next" in results is None.
        # Set continue iteration = False to break
        continue_iteration = True

        while continue_iteration:  # AND count < iteration_threshold

            # Regenerate Expires and Signatures for every call after the first one
            if current_page_number > 1:
                expires = int(time.time() + 20)
                # generate signature
                try:
                    signature = generate_signature(expires, constants.CTIX_ACCESS_ID, constants.CTIX_SECRET_KEY)
                except Exception as e:
                    logger.error(
                        "Fatal Error: Caught an exception while generating Authentication Signature: {}".format(e))
                    return
                else:
                    logger.debug("Authentication Signature Generated Successfully")

                params = {
                    "AccessID": constants.CTIX_ACCESS_ID,
                    "Expires": expires,
                    "Signature": signature
                }

            response = requests.get(next_page, params=params, verify=constants.CTIX_VERIFY_CERTIFICATE)
            # get response status
            status_code = response.status_code
            res = None

            if status_code == 200:
                # Get the response body
                res = response.json()
                # Append raw results to dataset
                ioc_data_set += res["results"]

                # Set Request Endpoint for next Iteration
                next_endpoint = constants.CTIX_SAVED_RESULT_SET_API_SUBSTITUTION_PATTERN.sub("/",
                                                                                             str(res["next"])).lstrip(
                    "/")
                next_page = "{}/ingestion/{}".format(next_page_base_url.rstrip("/"), next_endpoint)
                current_page_number += 1
                count += 1

            else:
                logger.error(
                    "Fatal Error: Encountered Error while fetching data from CTIX.\nStatus Code: {}, Message:{},"
                    "\nParams Passed: {}".format(
                        status_code, response.text, params))
                break

            if res["next"] is None:
                continue_iteration = False

    except requests.exceptions.Timeout:
        logger.error(
            "Fatal Error: Encountered Error while fetching data from CTIX.\nStatus Code: {}, \nException Encountered: "
            "{}".format(
                "408", "Request Timed Out"))
        # save checkpoint
        save_check_point("page_number_{}".format(constants.CTIX_INSTANCE_NAME), current_page_number)

    except requests.exceptions.RequestException as e:
        logger.error(
            "Fatal Error: Encountered Error while fetching data from CTIX. \nException Encountered: {}".format(e))
        # save checkpoint
        save_check_point("page_number_{}".format(constants.CTIX_INSTANCE_NAME), current_page_number)

    except Exception as e:
        logger.error(
            "Fatal Error: Encountered Error while fetching data from CTIX.\nStatus Code: {}, \nMessage:{}, \nException Encountered: {}".format(
                status_code, response.text, e))
        # save checkpoint
        save_check_point("page_number_{}".format(constants.CTIX_INSTANCE_NAME), current_page_number)

    else:
        logger.debug("Successfully received response from CTIX")
        # save checkpoints
        save_check_point("page_number_{}".format(constants.CTIX_INSTANCE_NAME), 0)
        save_check_point("last_run_date_{}".format(constants.CTIX_INSTANCE_NAME), int(time.time()))

    # format the indicators data
    indicators = []  # Hold formatted dataset
    for record in ioc_data_set:

        ctix_tags = ", ".join(str(tag["name"]) for tag in record.get("ctix_tags", []) if tag["name"])

        for indicator in record["data"]:
            try:
                # Extract only Indicator SDO
                if indicator.get("sdo_type", None) != "indicator":
                    continue

                indicator_data = {key: indicator.get(key, None) for key in constants.DATA_FIELDS_EXTRACTED}
                indicator_data["_key"] = indicator.get("sdo_name", None)
                indicator_data["indicator"] = indicator.get("sdo_name", None)
                indicator_data["indicator_type"] = indicator.get("indicator_type", {}).get("type", None)

                if "tlp" in indicator_data:
                    indicator_data["TLP"] = indicator.get('ctix_tlp')
                if "timestamp" in indicator_data:
                    indicator_data["timestamp"] = int(float(indicator.get("ctix_created")) * 1000)
                if "created_timestamp" in indicator_data:
                    indicator_data["created_timestamp"] = int(float(indicator.get("ctix_created")) * 1000)
                if "modified_timestamp" in indicator_data:
                    indicator_data["modified_timestamp"] = int(float(indicator.get("ctix_modified")) * 1000)
                if "score" in indicator_data:
                    indicator_data["score"] = indicator.get("ctix_score")
                if "sources" in indicator_data:
                    indicator_data["sources"] = ", ".join(
                        str(source["name"]) for source in indicator.get("sources", []) if source["name"])
                if "tags" in indicator_data:
                    indicator_data["tags"] = ctix_tags
                if "ctix_id" in indicator_data:
                    indicator_data["ctix_id"] = indicator.get("id", None)

                indicators.append(indicator_data)

            except Exception as e:
                logger.error(
                    "Fatal Error: Encountered Error while parsing data received from CTIX for Indicator:{}.\nStatus "
                    "Code: {}, \nException Encountered: {}".format(
                        indicator.get("sdo_name", "<indicator could not be extracted>"), status_code, e))

    logger.debug("Data Download Completed. Total Indicators downloaded: {}".format(len(indicators)))
    return indicators
