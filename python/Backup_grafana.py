import os
import requests
import json
from datetime import datetime

# Define helper functions
def create_directories(paths):
    for path in paths:
        try:
            os.makedirs(path, exist_ok=True)
            print(f"Directory created: {path}")
        except Exception as e:
            print(f"Error creating directory {path}: {e}")

def sanitize_filename(name):
    # Replace problematic characters in filenames
    return name.replace("/", "-").replace("\\", "-").replace("*", "").replace(":", "-").replace("?", "").replace("\"", "-").replace("<", "").replace(">", "").replace("|", "").strip()

# Initialize parameters
date = datetime.now().strftime("%d%m%y%H%M%S")
env = "ENV"
grafana_host = "URL"
api_token = "TOKEN"

main_dir = os.path.dirname(os.path.abspath(__file__))
env_dir = os.path.join(main_dir, f"Grafana_backup/{env}_{date}")
summary_dir = os.path.join(env_dir, "Summary")
alert_dir_all = os.path.join(env_dir, "grafana_alerts/all")
dashboard_dir = os.path.join(env_dir, "grafana_dashboards")
datasource_dir = os.path.join(env_dir, "grafana_datasource")
contact_points_dir_all = os.path.join(env_dir, "grafana_contactPoints/All")
notification_policy_tree_dir = os.path.join(env_dir, "grafana_notificationPolicyTree")
mute_timings_dir_all = os.path.join(env_dir, "grafana_muteTimings/All")
templates_dir = os.path.join(env_dir, "grafana_templates")

# Create backup directory structure
create_directories([
    env_dir,
    summary_dir,
    alert_dir_all,
    dashboard_dir,
    datasource_dir,
    contact_points_dir_all,
    notification_policy_tree_dir,
    mute_timings_dir_all,
    templates_dir
])

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

def fetch_and_save(endpoint, filepath, is_json=True):
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json() if is_json else response.text
        with open(filepath, "w", encoding="utf-8") as f:
            if is_json:
                json.dump(data, f, indent=4)
            else:
                f.write(data)
        print(f"Data saved to {filepath}")
    except Exception as e:
        print(f"Error fetching data from {endpoint}: {e}")

# Define endpoints
alert_endpoint = f"{grafana_host}/api/v1/provisioning/alert-rules"
alert_export_endpoint = f"{grafana_host}/api/v1/provisioning/alert-rules/export"
contact_points_endpoint = f"{grafana_host}/api/v1/provisioning/contact-points"
contact_points_export_endpoint = f"{grafana_host}/api/v1/provisioning/contact-points/export"
notification_policy_tree_endpoint = f"{grafana_host}/api/v1/provisioning/policies"
notification_policy_tree_export_endpoint = f"{grafana_host}/api/v1/provisioning/policies/export"
mute_timings_endpoint = f"{grafana_host}/api/v1/provisioning/mute-timings"
mute_timings_export_endpoint = f"{grafana_host}/api/v1/provisioning/mute-timings/export"
templates_endpoint = f"{grafana_host}/api/v1/provisioning/templates"
dashboard_search_endpoint = f"{grafana_host}/api/search?query="
dashboard_detail_endpoint = f"{grafana_host}/api/dashboards/uid"
datasource_endpoint = f"{grafana_host}/api/datasources"

# Fetch and save alerts
fetch_and_save(alert_endpoint, os.path.join(alert_dir_all, "alert-rules.json"))
fetch_and_save(alert_export_endpoint, os.path.join(alert_dir_all, "alert-rules-export.json"))

# Fetch and save contact points
fetch_and_save(contact_points_export_endpoint, os.path.join(contact_points_dir_all, "contactPointsExport.yaml"), is_json=False)
fetch_and_save(contact_points_endpoint, os.path.join(contact_points_dir_all, "contactPointsExport.json"))

# Fetch and save notification policy tree
fetch_and_save(notification_policy_tree_export_endpoint, os.path.join(notification_policy_tree_dir, "notificationPolicyTreeExport.yaml"), is_json=False)
fetch_and_save(notification_policy_tree_endpoint, os.path.join(notification_policy_tree_dir, "notificationPolicyTreeExport.json"))

# Fetch and save mute timings
fetch_and_save(mute_timings_export_endpoint, os.path.join(mute_timings_dir_all, "muteTimingsExport.yaml"), is_json=False)
fetch_and_save(mute_timings_endpoint, os.path.join(mute_timings_dir_all, "muteTimingsExport.json"))

# Fetch and save templates
fetch_and_save(templates_endpoint, os.path.join(templates_dir, "templatesExport.json"))

# Fetch and process dashboards
try:
    response = requests.get(dashboard_search_endpoint, headers=headers)
    response.raise_for_status()
    dashboards = response.json()

    for dashboard in dashboards:
        uid = dashboard.get("uid")
        title = sanitize_filename(dashboard.get("title", "unknown"))

        # Fetch dashboard details
        try:
            detail_response = requests.get(f"{dashboard_detail_endpoint}/{uid}", headers=headers)
            detail_response.raise_for_status()
            dashboard_data = detail_response.json()

            # Determine folder structure
            folder_title = sanitize_filename(dashboard_data.get("meta", {}).get("folderTitle", "General"))
            folder_path = os.path.join(dashboard_dir, folder_title)
            create_directories([folder_path])

            # Save dashboard JSON
            filepath = os.path.join(folder_path, f"{title}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(dashboard_data, f, indent=4)
            print(f"Dashboard saved: {filepath}")

        except Exception as e:
            print(f"Error fetching dashboard details for {title} (UID: {uid}): {e}")

except Exception as e:
    print(f"Error fetching dashboards: {e}")

# Fetch and save datasources
fetch_and_save(datasource_endpoint, os.path.join(summary_dir, "datasources.csv"), is_json=False)

# Fetch and save individual datasources
try:
    response = requests.get(datasource_endpoint, headers=headers)
    response.raise_for_status()
    datasources = response.json()
    for datasource in datasources:
        uid = datasource.get("uid")
        name = sanitize_filename(datasource.get("name", "unknown"))
        filepath = os.path.join(datasource_dir, f"{name}.json")
        fetch_and_save(f"{datasource_endpoint}/{uid}", filepath)
except Exception as e:
    print(f"Error fetching datasources: {e}")

# Summary
print("Backup Summary")
