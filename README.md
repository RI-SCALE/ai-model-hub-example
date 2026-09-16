# ai-model-hub-example

Example upload script to upload a bioengine model.

## Setup

1. Clone the repository:

   ```bash
   git clone git@github.com:aicell-lab/ai-model-hub-example.git
   ```

2. Navigate to the project directory:

   ```bash
   cd ai-model-hub-example
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and set your API token:

   ```bash
   cp .env.example .env
   ```

   Set `HYPHA_TOKEN` to your actual API token (replace `<your_api_token_here>`).
   This is the variable name the upload script reads. Generate a token by logging
   in at https://modelhub.riscale.eu and using the token controls on the Upload
   page (`/#/upload`). For long-running or HPC jobs, pick a longer expiry.

5. Modify the `manifest.yaml` file in the desired model folder (e.g., `model_example1`) to set the correct `id` field:

   ```yaml
   id: your_model_id_here
   ```

6. Run the upload script:

   ```bash
   python upload_model.py model_example1
   ```

7. (Optional) Upload from a different folder:

   ```bash
   python upload_model.py <folder_name>
   ```
