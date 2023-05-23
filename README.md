# Configure CTIX App for Humio

Download this CTIX app package on your local server to define the CTIX-Humio integration constants and run the app to fetch CTIX data.

## Define Integration Constants

Define the CTIX-Humio integration constants to establish the connection between your CTIX and Humio apps. In the CTIX app package, open the constants.py file under config and define the following constants:

* CTIX_INSTANCE_NAME: Enter the instance name of your CTIX application. For example, ctix_prod.
* CTIX_BASE_URL: Enter the endpoint URL of your CTIX application. For example, https://prod.cyware.com/ctixapi/.
* CTIX_ACCESS_ID: Enter the access ID of your CTIX application.
* CTIX_SECRET_KEY: Enter the secret key of your CTIX application.
* HUMIO_BASE_URL: Enter the base URL of your Humio application. For example, https://cloud.us.humio.com/.
* HUMIO_HEC_BEARER_TOKEN: Enter the ingest token of your Humio application that you created

For more information on how to generate the API credentials in CTIX, see [Generate Open API Credentials](https://techdocs.cyware.com/en/299670-447852-configure-open-api.html#UUID-8cf6c276-1af8-65fb-5fd1-995a016a7703_section-idm4659587550920033321460492648).

For more information on how to generate an ingest token in Humio, see [Generate a New Ingest Token](https://library.humio.com/falcon-logscale/ingesting-data-tokens.html#ingesting-data-tokens-generate).

## Schedule Cron Job

To schedule a cron job to run the CTIX app every minute and retrieve CTIX data into Humio, do the following:

1. Run crontab -e to create a crontab.
2. Enter the following cron expression and save: * * * * * /usr/bin/python &lt;ctix app package directory>/ctix_to_humio.py.
