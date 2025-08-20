import os
import asyncio
import argparse
from typing import Any
from venv import logger
import httpx
from hypha_rpc import connect_to_server
from hypha_rpc.rpc import RemoteService, RemoteException
from dotenv import load_dotenv


async def ensure_artifact_exists(
    artifact_manager: RemoteService, **kwargs: Any
) -> dict[str, Any]:
    try:
        return await artifact_manager.create(**kwargs)
    except RemoteException:
        artifact_id = kwargs.get("alias")
        manifest = await artifact_manager.read(artifact_id=artifact_id)
        logger.info("Artifact already exists")
        return manifest


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


async def upload_model(model_name: str, directory: str | None = None):
    if directory is None:
        directory = model_name

    load_dotenv()

    server_config = {
        "server_url": "https://hypha.aicell.io",
        "workspace": "ri-scale",
        "token": os.getenv("HYPHA_API_TOKEN"),
    }

    async with connect_to_server(server_config) as server:
        artifact_manager: RemoteService = await server.get_service(  # type: ignore
            "public/artifact-manager"
        )

        model_manifest = {
            "name": model_name,
            "description": f"AI model for {model_name}",
        }

        await ensure_artifact_exists(
            artifact_manager=artifact_manager,
            parent_id="ai-model-hub",
            alias=model_name,
            type="model",
            manifest=model_manifest,
        )

        await artifact_manager.edit(artifact_id=model_name, stage=True)

        await upload_directory(
            artifact_manager=artifact_manager,
            directory=directory,
            artifact_id=model_name,
        )

        await artifact_manager.commit(artifact_id=model_name)


def main():
    parser = argparse.ArgumentParser(description="Upload model dataset to Hypha")
    parser.add_argument("model_name", type=str, help="Name of the model to upload")
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        help="Directory of the model dataset to upload",
    )
    args = parser.parse_args()

    asyncio.run(upload_model(args.model_name, args.directory))


if __name__ == "__main__":
    main()
