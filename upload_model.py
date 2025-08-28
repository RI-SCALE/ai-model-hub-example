import argparse
import asyncio
import logging
import os

import httpx
import yaml
from dotenv import load_dotenv
from hypha_rpc import connect_to_server, login  # type: ignore
from hypha_rpc.rpc import RemoteException  # type: ignore
from hypha_rpc.utils import ObjectProxy  # type: ignore

logger = logging.getLogger(__name__)


async def upload_directory(
    artifact_manager: ObjectProxy, directory: str, artifact_id: str
):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        put_file_url = await artifact_manager.put_file(  # type: ignore
            artifact_id=artifact_id,
            file_path=filename,
        )

        if not isinstance(put_file_url, str):
            raise ValueError("Expected put_file_url to be a string")

        with open(file_path, "rb") as f:
            content = f.read()
            async with httpx.AsyncClient() as client:
                response = await client.put(put_file_url, content=content)

                if response.status_code != 200:
                    logger.error("Failed to upload %s: %s", filename, response.text)

                response.raise_for_status()


async def upload_model(model_dir: str):

    load_dotenv()

    server_url = os.getenv("HYPHA_SERVER_URL") or "https://hypha.aicell.io"
    token: str = os.getenv("HYPHA_TOKEN") or await login({"server_url": server_url})  # type: ignore
    workspace = "ri-scale"

    server_config: dict[str, str] = {
        "server_url": server_url,
        "token": token,
    }

    async with connect_to_server(server_config) as server:  # type: ignore
        artifact_manager: ObjectProxy = await server.get_service(  # type: ignore
            "public/artifact-manager"
        )

        if not isinstance(artifact_manager, ObjectProxy):
            raise ValueError("Expected artifact_manager to be a ObjectProxy")

        with open(os.path.join(model_dir, "manifest.yaml"), "r") as f:
            model_manifest = yaml.safe_load(f)

        model_id = model_manifest["id"]
        full_parent_id = f"{workspace}/ai-model-hub"
        full_artifact_id = f"{workspace}/{model_id}"

        try:
            await artifact_manager.create(  # type: ignore
                parent_id=full_parent_id,
                workspace=workspace,
                alias=model_id,
                stage=True,
                manifest=model_manifest,
            )
        except RemoteException:
            print("Artifact already exists.")
            await artifact_manager.edit(  # type: ignore
                artifact_id=full_artifact_id, manifest=model_manifest, stage=True
            )

        await upload_directory(
            artifact_manager=artifact_manager,
            directory=model_dir,
            artifact_id=full_artifact_id,
        )

        await artifact_manager.commit(artifact_id=full_artifact_id)


def main():
    parser = argparse.ArgumentParser(description="Upload model dataset to Hypha")
    parser.add_argument("model_dir", type=str, help="Directory of the model to upload")
    args = parser.parse_args()

    asyncio.run(upload_model(args.model_dir))


if __name__ == "__main__":
    main()
