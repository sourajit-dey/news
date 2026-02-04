# 🇮🇳 Truth Engine India

An automated AI system that scans Google Trends, verifies viral news using Gemini, and publishes debunking reports to a static website and Twitter (X).

## 🌍 Where is my website?
Your website will be live at:
**[https://sourajit-dey.github.io/news](https://sourajit-dey.github.io/news)**

### 🚨 ACTIVATE IT NOW:
1.  Go to your GitHub Repo **Settings** (top right tab).
2.  Click **"Pages"** on the left sidebar.
3.  Under **"Build and deployment"** > **"Branch"**:
    *   Select `main` (or `master`) as the branch.
    *   Select `/ (root)` folder.
    *   Click **Save**.
4.  Wait 1-2 minutes. Your site is now online!

---

## 🤖 How it works (The "Brain")
The system runs entirely on **GitHub Actions** (in the cloud) for free, every hour.

1.  **Scans:** Checks top 3 trending topics in India on Google.
2.  **Verifies:** Sends search results to **Gemini AI** to check for misinformation.
3.  **Decides:**
    *   **Fake News / Misleading:** It **Tweets** an alert 🔴 and adds it to the Website.
    *   **Verified / Neutral:** It ignores it (to avoid spamming).
4.  **Publishes:**
    *   Updates `db.json` (the database).
    *   Re-builds `index.html`.
    *   Commits changes back to this repo.

---

## 🎮 How to Control It

### 1. Stop the Bot
*   Go to **Actions** tab -> **Daily Truth Check**.
*   Click the **"..." (three dots)** top right -> **Disable workflow**.

### 2. Manually Run It
*   Go to **Actions** tab -> **Daily Truth Check**.
*   Click **Run workflow**.

### 3. Edit/Delete News
*   The "Database" is just a file named `db.json`.
*   Click on `db.json` in your repo code.
*   Click the **Pencil Icon** (Edit).
*   Delete the block of text for the news item you want to remove.
*   **Commit Changes**.
*   (The site will update automatically the next time the bot runs, or you can run it manually).

### 4. Update Cookies (If Twitter Login Fails)
*   Twitter cookies expire every few months.
*   If tweets stop working, update the `TWITTER_AUTH_TOKEN` in **Settings > Secrets**.
