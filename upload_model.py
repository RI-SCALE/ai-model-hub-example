import argparse
import asyncio
import logging
import os

import httpx
import yaml
from dotenv import load_dotenv
from hypha_artifact import AsyncHyphaArtifact  # type: ignore
from hypha_rpc import login  # type: ignore

logger = logging.getLogger(__name__)


async def upload_model(model_dir: str):

    load_dotenv()

    server_url = os.getenv("HYPHA_SERVER_URL") or "https://hypha.aicell.io"
    token: str = os.getenv("HYPHA_API_TOKEN") or await login({"server_url": server_url})  # type: ignore
    workspace = "ri-scale"

    if not isinstance(token, str):
        raise ValueError("Token must be a string")

    with open(os.path.join(model_dir, "manifest.yaml"), "r") as f:
        model_manifest = yaml.safe_load(f)

    model_id = model_manifest["id"]

    parent_artifact = AsyncHyphaArtifact(
        artifact_id=f"{workspace}/ai-model-hub",
        server_url=server_url,
        token=token,
        workspace=workspace,
    )

    try:
        await parent_artifact.create(model_manifest, stage=False)
    except httpx.RequestError:
        log_msg = f"Artifact {parent_artifact.artifact_id} likely already exists."
        logger.info(log_msg)

    hypha_artifact = AsyncHyphaArtifact(
        artifact_id=f"{workspace}/{model_id}",
        server_url=server_url,
        token=token,
        workspace=workspace,
    )

    try:
        await hypha_artifact.create(model_manifest, stage=True)
    except httpx.RequestError:
        log_msg = f"Artifact {hypha_artifact.artifact_id} likely already exists."
        logger.info(log_msg)
        await hypha_artifact.edit(model_manifest, stage=True)

    await hypha_artifact.put(model_dir, recursive=True)

    await hypha_artifact.commit()


def main():
    parser = argparse.ArgumentParser(description="Upload model dataset to Hypha")
    parser.add_argument("model_dir", type=str, help="Directory of the model to upload")
    args = parser.parse_args()

    asyncio.run(upload_model(args.model_dir))


if __name__ == "__main__":
    main()
