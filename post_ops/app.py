"""
    Classe che si occupa della pipeline di post processing.
    Lo scopo è:
    -1 attuare eventuali funzioni di correzione dati (correlazione con temperatura etc);
    -2 caricare i dati su Azure (PREDIS)

    L'app viene eseguita come client di mercure, di conseguenza il suo scopo è quello di ascoltare le push di mercure e,
    più nello specifico, ascolta i messaggi sul topic [predis_dev_measure] sul quale vengono pubblicate tutte le misure
    fatte da ogni device.
"""
import json
import logging
import os
import sys

import dotenv
from azure.storage.blob import BlobServiceClient
from sseclient import SSEClient

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s]: {} %(levelname)s %(message)s'.format(os.getpid()),
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[logging.StreamHandler()])
    logger = logging.getLogger()
    logger.info(f'Starting app')

    dotenv.load_dotenv()

    predis_env = os.environ.get("APP_MODE")
    exclude_devs = ['PREDIS001', 'PREDIS002', 'PREDIS003', 'PREDIS004', 'PREDIS005']
    token = os.environ.get("MERCURE_TOKEN")
    updates = SSEClient(
        os.environ.get("MERCURE_HUB"),
        params={"topic": [os.environ.get('MERCURE_TOPIC')]},
        headers={"Authorization": "Bearer " + token},
    )

    # azure connection string
    connect_str = os.getenv('AZURE_CONNECTION_STRING')
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    except Exception as e:
        logging.error(f'impossibile connettersi ad azure: {e}')
        sys.exit(0)

    container_name = os.environ.get('AZURE_CONTAINER')
    logging.info(f'app mode: {predis_env}, container name: {container_name}, exclude devs: {exclude_devs}')
    for update in updates:
        logging.info(f"Update received: {update}")
        try:
            obj = json.loads(update.data)
            if obj['devname'] not in exclude_devs:
                local_file_name = obj['filename'].split('/')[-1] + '.txt'
                devname_folder = obj['devname']
                path = f'{devname_folder}/{local_file_name}'
                logging.info(f'path: {path}')
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=path)
                logging.info("\nUploading to Azure Storage as blob:\n\t" + local_file_name)
                try:
                    with open(file=obj["filename"], mode="rb") as data:
                        blob_client.upload_blob(data)
                except Exception as e:
                    logging.error(f'errore scrittura')
                logging.info("done")
            else:
                logging.info(f'Escludo caricamento per {obj["devname"]}')
        except Exception as e:
            logging.info(f"exception: {e}")
