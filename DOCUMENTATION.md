# Library Documentation

## Developing Documentation

This project uses `mkdocs` and `mkdocs-material` to generate the documentation. To work on the documentation locally, follow these steps:

1.  **Install dependencies:**
    Make sure you have all the required packages installed, including the ones for documentation.

    ```bash
    pip install -r requirements.txt
    ```

2.  **Serve the documentation:**
    Run the following command from the root of the project to start a local development server:

    ```bash
    mkdocs serve
    ```

3.  **View the documentation:**
    Open your web browser and navigate to `http://127.0.0.1:8000` to see the documentation. The server will automatically reload the site whenever you make changes to the markdown files in the `docs/` directory.

## Automated Documentation Deployment

The documentation for this project is automatically built and deployed to GitHub Pages using a GitHub Actions workflow.

### Workflow Overview

The workflow is defined in the file `.github/workflows/ci.yml` and consists of two main jobs: `build` and `deploy`.

1.  **Trigger**: The workflow is automatically triggered on every `push` to the `main` branch.

2.  **Build Job**:
    - Checks out the repository's code.
    - Sets up the correct Python environment.
    - Installs the necessary dependencies, including `mkdocs-material`.
    - Runs the `mkdocs build` command to generate the static HTML site from the Markdown files in the `docs/` directory.
    - Uploads the generated `site/` directory as a GitHub Pages artifact.

3.  **Deploy Job**:
    - This job waits for the `build` job to complete successfully.
    - It downloads the artifact created by the `build` job.
    - It then uses the `actions/deploy-pages@v4` action to deploy the contents of the artifact to GitHub Pages.

This process ensures that the documentation available online is always up-to-date with the latest changes in the `main` branch.
