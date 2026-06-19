# 🎬 YouTube Title Stats Updater

Automatically updates your YouTube video title every 10 minutes with real‑time stats:  
Views, Likes, and Comment count.

Built with Python, Flask, and the YouTube Data API v3.  
Optimised to stay within the free API quota (10,000 units/day).

---

## ✨ Features

- 🔢 Shows view count in the title  
- ❤️ Shows like count  
- 💬 Shows comment count  
- ⏱️ Runs every 10 minutes (adjustable)  
- 🔐 Uses OAuth 2.0 – secure and personal  
- 🧩 Keeps your video description, tags, and category unchanged  
- 📝 Logs all updates to update_log.txt  
- 🚀 Ready to deploy on Render.com with a free Keep‑Alive using cron‑job.org

---

## 🛠️ Prerequisites

- Python 3.7 or higher  
- A Google Cloud project with the YouTube Data API v3 enabled  
- OAuth 2.0 credentials (client_secrets.json) – download as a Desktop app

---

## 📦 Installation

1. Clone the repository (or download the files):

       git clone https://github.com/your-username/youtube-title-stats-updater.git
       cd youtube-title-stats-updater

2. Install the required packages:

       pip install -r requirements.txt

3. Place your client_secrets.json in the project folder (this file contains your OAuth credentials).

4. Edit app.py and replace:

       VIDEO_ID = 'YOUR_VIDEO_ID_HERE'

   with your actual video ID (the part after ?v= in the YouTube URL).

---

## ▶️ Run Locally

       python app.py

The first time you run it, a browser window will open asking you to log in to your Google account and grant permission.  
After that, a token.pickle file is created so you don't have to log in again.

You should see output like:

       ✅ Authentication successful. Starting update loop...
       2025-06-19 14:30:00 ✅ Updated: views=1,234, likes=56, comments=12

---

## ☁️ Deploy on Render.com (Free)

1. Push your code to a GitHub repository.
2. Log in to Render.com and create a new Web Service.
3. Connect your GitHub repo.
4. Use these settings:
   - Environment: Python
   - Build Command: pip install -r requirements.txt
   - Start Command: python app.py
   - Instance Type: Free
5. Click Create Web Service.
6. After deployment, you'll get a URL like https://your-app.onrender.com.

---

## ⏰ Keep‑Alive (Prevent Sleeping)

Render’s free plan spins down services after 15 minutes of inactivity.  
To keep yours awake 24/7, use cron-job.org:

- Create a new cron job.
- Set the URL to your Render URL (e.g., https://your-app.onrender.com).
- Set the schedule to every 10 minutes.
- Save it.

Now your script will run indefinitely.

---

## ⚙️ Adjust the Update Interval

Open app.py and change the UPDATE_INTERVAL_MINUTES variable (line ~28):

       UPDATE_INTERVAL_MINUTES = 10   # Change to any value (in minutes)

Quota reminder:  
Each run costs 51 units (1 for fetching stats + 50 for updating the title).  
With 10‑minute intervals: 144 runs/day → 7,344 units/day (under the 10,000 free limit).  
If you set it below 7 minutes, you risk exceeding the daily quota.

---

## 📂 Project Structure

       youtube-title-stats-updater/
       ├── app.py                # Main script
       ├── requirements.txt      # Dependencies
       ├── client_secrets.json   # Your OAuth credentials (keep secret!)
       ├── .gitignore            # Excludes secrets and logs
       └── README.md             # This file

---

## 🤝 Contributing

Feel free to fork this project and submit pull requests.  
For major changes, please open an issue first to discuss what you would like to change.

---

## 📝 License

This project is licensed under the MIT License – see the LICENSE file for details.

---

## ⚠️ Disclaimer

This script uses the YouTube Data API and is subject to Google’s terms of service.  
The author is not responsible for any misuse or quota overages. Use responsibly.
