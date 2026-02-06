# Deployment Guide: Hugging Face Spaces

Since your application uses **FastAPI** (Python) with a **Custom HTML/JS Frontend**, the best way to deploy it is using **Hugging Face Spaces** with the **Docker** SDK.

This preserves your exact architecture without needing to rewrite the frontend for Streamlit or configure serverless functions for Vercel.

## Step 1: Prepare Files (Already Done)
I have created a `Dockerfile` in your project folder. This tells Hugging Face how to build your app.

**Key Settings in Dockerfile:**
- **Port**: `7860` (Hugging Face's default port).
- **Command**: Runs `mock_uhc_api:app`.

## Step 2: Create a New Space
1.  Go to [huggingface.co/new-space](https://huggingface.co/new-space).
2.  **Space Name**: `uhc-prior-auth-agent` (or similar).
3.  **License**: `Apache 2.0` (or your choice).
4.  **SDK**: Select **Docker** (Important!).
5.  **Visibility**: Public or Private.
6.  Click **Create Space**.

## Step 3: Upload Code
You can upload via the Web UI or Git. Since you already have a local git repo:

**Option A: Git Command Line (Recommended)**
1.  Hugging Face will show you a git clone command (e.g., `git clone https://huggingface.co/spaces/username/uhc-agent`).
2.  Add the Hugging Face remote to your current repo:
    ```bash
    git remote add space https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
    ```
3.  Push your code:
    ```bash
    git push space main
    ```
    *(You may need to `git pull space main --allow-unrelated-histories` first if the space isn't empty).*

**Option B: Web Upload**
1.  In your new Space, go to the **Files** tab.
2.  Click **Add file** -> **Upload files**.
3.  Drag and drop **ALL** your files (agents/, static/, mock_uhc_api.py, requirements.txt, Dockerfile, etc.).
4.  Click **Commit changes**.

## Step 4: Live Check
Hugging Face will build the container (takes ~2 minutes). Once "Running":
- Your frontend will be live at `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`.
- The API will be working behind the scenes.
