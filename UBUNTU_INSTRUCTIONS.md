# 🐧 Running on Ubuntu / Linux

This guide will help you set up and run the Twitter Sentiment Analysis project on an Ubuntu machine (e.g., Lab Computer).

## 1. Prerequisites (Run these once)
Open a terminal and install the required software:

```bash
sudo apt update
sudo apt install -y openjdk-17-jdk python3-pip python3-venv git
```

## 2. Clone the Repository
Download the project code:

```bash
git clone https://github.com/ashwinsureshh/twitter-sentiment-analysis.git
cd twitter-sentiment-analysis
```

## 3. Setup Python Environment
Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-working.txt
```

## 4. Download the Dataset
⚠️ **Important**: The dataset is too large for GitHub. You must add it manually.
1.  Download **Sentiment140** (or use the sample provided).
2.  Ensure the file is named `source_tweets.csv`.
3.  Place it inside the `dataset/` folder.
    *   Path: `twitter-sentiment-analysis/dataset/source_tweets.csv`

## 5. Run the Project
We have a special script for Ubuntu that handles everything:

```bash
chmod +x quick-start-ubuntu.sh
./quick-start-ubuntu.sh
```

## 6. View the Dashboard
Open Firefox or Chrome and go to:
👉 **http://localhost:8501**

---

## 🛠 Troubleshooting

**"Port 9999 already in use"**
If the script fails saying the port is busy, run this to clear it:
```bash
lsof -ti:9999 | xargs kill -9
```

**"Java not found"**
Ensure Java 17 is selected:
```bash
sudo update-alternatives --config java
# Select the number corresponding to java-17-openjdk
```
