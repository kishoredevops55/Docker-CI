import requests
from datetime import datetime, timedelta
import os

repo_owner = os.getenv("REPO_OWNER")
repo_name = os.getenv("REPO_NAME")
token = os.getenv("GITHUB_TOKEN")
days_old = int(os.getenv("DAYS_OLD"))

# GitHub API URLs
branches_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/branches"
delete_branch_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/refs/heads/"
protected_branches_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/branches"

# Headers for authentication
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

# Get the list of protected branches
protected_branches_response = requests.get(protected_branches_url, headers=headers)
protected_branches = [branch['name'] for branch in protected_branches_response.json() if branch.get('protected')]

# Get the list of branches
response = requests.get(branches_url, headers=headers)
branches = response.json()

# Check each branch
for branch in branches:
    branch_name = branch['name']
    if branch_name in protected_branches:
        continue

    branch_info_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/branches/{branch_name}"
    branch_info_response = requests.get(branch_info_url, headers=headers)
    branch_info = branch_info_response.json()

    # Get the commit date
    commit_date_str = branch_info['commit']['commit']['committer']['date']
    commit_date = datetime.strptime(commit_date_str, '%Y-%m-%dT%H:%M:%SZ')

    # Calculate the age of the branch
    branch_age = datetime.now() - commit_date

    # Delete if older than specified number of days
    if branch_age > timedelta(days=days_old):
        delete_response = requests.delete(delete_branch_url + branch_name, headers=headers)
        if delete_response.status_code == 204:
            print(f"Deleted branch: {branch_name}")
        else:
            print(f"Failed to delete branch: {branch_name} - {delete_response.status_code}")

print("Completed checking and deleting old branches.")

