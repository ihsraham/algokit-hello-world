import logging
from base64 import b64decode
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
import algokit_utils

logger = logging.getLogger(__name__)

def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    app_spec: algokit_utils.ApplicationSpecification,
    deployer: algokit_utils.Account,
) -> None:
    from smart_contracts.artifacts.hello_world.hello_world_client import HelloWorldClient

    app_client = HelloWorldClient(
        algod_client,
        creator=deployer,
        indexer_client=indexer_client,
    )

    app_client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
        on_update=algokit_utils.OnUpdate.AppendApp,
    )
    
    name = "Maharshi Mishra"
    
    def call_method(method, *args, **kwargs):
        try:
            response = method(*args, **kwargs)
            logger.info(f"Called {method.__name__} on {app_spec.contract.name} ({app_client.app_id}), received: {response.return_value}")
            
            # Wait for transaction confirmation
            algod_client.status_after_block(response.confirmed_round)
            logger.info(f"Transaction confirmed in round: {response.confirmed_round}")
            
            return response.return_value
        except Exception as e:
            logger.error(f"Error calling {method.__name__}: {str(e)}")
            return None

    # Call hello method
    call_method(app_client.hello, name=name, transaction_parameters=algokit_utils.TransactionParameters(boxes=[(0, b"greeting"), (0, b"initialized")]))

    # Log application info and box contents
    log_app_and_box_info(algod_client, app_client.app_id, ["greeting", "initialized"])

    # Call other methods
    call_method(app_client.is_initialized, transaction_parameters=algokit_utils.TransactionParameters(boxes=[(0, b"initialized")]))
    call_method(app_client.read_greeting, transaction_parameters=algokit_utils.TransactionParameters(boxes=[(0, b"greeting"), (0, b"initialized")]))

def log_app_and_box_info(algod_client: AlgodClient, app_id: int, box_names: list[str]):
    try:
        app_info = algod_client.application_info(app_id)
        logger.info(f"Application info for app {app_id}:")
        logger.info(f"Creator: {app_info['params']['creator']}")
        logger.info(f"Address: {app_info['params'].get('address', 'Not available')}")

        for box_name in box_names:
            try:
                box_content = algod_client.application_box_by_name(app_id, box_name.encode())
                decoded_content = b64decode(box_content['value']).decode('utf-8')
                logger.info(f"Box '{box_name}' content: {decoded_content}")
            except Exception as box_error:
                logger.warning(f"Could not retrieve content for box '{box_name}': {str(box_error)}")
    except Exception as e:
        logger.error(f"Error fetching application info for app {app_id}: {str(e)}")
