# 🧟‍♂️ Azure Zombie Hunter

**Status:** Active | **License:** MIT | **Author:** Dinesh Perabathula

### ⚡ The Problem
Cloud waste is silent. Companies lose thousands of dollars on "Zombie" resources—Managed Disks and IPs that are unattached but still billing.

### 🛠 The Solution
Azure Zombie Hunter is a lightweight, Python-based utility that:
1.  **Authenticates** securely using Azure Identity.
2.  **Scans** your subscription for unattached/idle resources.
3.  **Reports** potential savings immediately.

### 🚀 Quick Start (Cloud Shell)
Run this directly in Azure Cloud Shell (Bash):

```bash
# 1. Clone the repo
git clone git@github.com:Dineshpera/azure-zombie-hunter.git
cd azure-zombie-hunter

# 2. Install dependencies
pip install --user -r requirements.txt

# 3. Hunt
python hunter.py
