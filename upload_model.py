import argparse
import asyncio
import logging
import os

import httpx
import yaml
from dotenv import load_dotenv
from hypha_rpc import connect_to_server, login
from hypha_rpc.rpc import RemoteException, RemoteService

logger = logging.getLogger(__name__)


async def upload_directory(
    artifact_manager: RemoteService, directory: str, artifact_id: str
):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        put_file_url = await artifact_manager.put_file(
            artifact_id=artifact_id,
            file_path=filename,
        )
        with open(file_path, "rb") as f:
            content = f.read()
            async with httpx.AsyncClient() as client:
                response = await client.put(put_file_url, content=content)

                if response.status_code != 200:
                    logger.error("Failed to upload %s: %s", filename, response.text)

                response.raise_for_status()


async def upload_model(model_dir: str | None = None):

    load_dotenv()

    server_url = os.getenv("HYPHA_SERVER_URL") or "https://hypha.aicell.io"
    token = os.getenv("HYPHA_TOKEN") or await login({"server_url": server_url})

    server_config = {
        "server_url": server_url,
        "token": token,
    }

    async with connect_to_server(server_config) as server:
        artifact_manager: RemoteService = await server.get_service(  # type: ignore
            "public/artifact-manager"
        )

        with open(os.path.join(model_dir, "manifest.yaml"), "r") as f:
            model_manifest = yaml.safe_load(f)

        model_id = model_manifest["id"]

        try:
            await artifact_manager.create(
                parent_id="ri-scale/ai-model-hub",
                workspace="ri-scale",
                alias=model_id,
                stage=True,
                manifest=model_manifest,
            )
        except RemoteException:
            print("Artifact already exists.")
            await artifact_manager.edit(
                artifact_id=f"ri-scale/{model_id}", manifest=model_manifest, stage=True
            )

        await upload_directory(
            artifact_manager=artifact_manager,
            directory=model_dir,
            artifact_id=model_id,
        )

        # await artifact_manager.commit(artifact_id=model_id)


def main():
    parser = argparse.ArgumentParser(description="Upload model dataset to Hypha")
    parser.add_argument("model_dir", type=str, help="Directory of the model to upload")
    args = parser.parse_args()

    asyncio.run(upload_model(args.model_dir))


if __name__ == "__main__":
    main()
