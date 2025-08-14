# bioengine-example

Example upload script of bioengine

## Setup

1. Clone the repository:

   ```bash
   git clone git@github.com:aicell-lab/bioengine-example.git
   ```

2. Navigate to the project directory:

   ```bash
   cd bioengine-example
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and set your API token:

   ```bash
   cp .env.example .env
   ```

   Replace <your_api_token_here> with your actual API token.

5. Run the upload script:

   ```bash
   python upload_model.py cellpose-finetuning
   ```

6. (Optional) Upload different model

   To upload a different model, use this command format:

   ```bash
   python upload_model.py <model_name>
   ```

   Or if you want to specify a different model directory:

   ```bash
   python upload_model.py <model_name> <model_directory>
   ```
