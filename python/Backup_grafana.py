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

# Replace problematic characters in filenames
def sanitize_filename(name, max_lenght=255):
    sanitazed = name.replace("/", "-").replace("\\", "-").replace("*", "").replace(":", "-").replace("?", "").replace("\"", "-").replace("<", "").replace(">", "").replace("|", "").strip()
    return sanitazed[:max_lenght]


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

def more_detailed_fetch_and_save(endpoint, endpoint_dir, uid_key, title_key, is_folder=False):
    """
    Fetches data from an endpoint, creates a folder structure (if required), and saves detailed data to files.

    :param endpoint: URL of the endpoint to fetch data from.
    :param endpoint_dir: Base directory to save the fetched data.
    :param uid_key: Key in the JSON response that uniquely identifies each item (e.g., "uid").
    :param title_key: Key in the JSON response that provides the title/name for the file or folder (e.g., "title").
    :param is_folder: Whether to create a folder structure based on the data (True/False).
    """
    try:
        # Fetch all items from the given endpoint
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        all_data = response.json()

        for single_data in all_data:
            # Extract unique identifier and sanitized title for the file/folder
            identity = single_data.get(uid_key)
            title_name = sanitize_filename(single_data.get(title_key, "unknown"))

            try:
                # Fetch detailed data for each item
                detail_response = requests.get(f"{endpoint}/{identity}", headers=headers)
                detail_response.raise_for_status()
                gathered_single_data = detail_response.json()

                # Create folder structure if `is_folder` is True
                if is_folder:
                    folder_title = sanitize_filename(gathered_single_data.get("meta", {}).get("folderTitle", "General"))
                    folder_path = os.path.join(endpoint_dir, folder_title)
                    create_directories([folder_path])

                    # Define the filepath for saving the JSON data
                    filepath = os.path.join(folder_path, f"{title_name}.json")
                else:
                    # If no folder structure is required, save directly to the base directory
                    filepath = os.path.join(endpoint_dir, f"{title_name}.json")

                # Save the detailed data to a JSON file
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(gathered_single_data, f, indent=4)

                print(f"Data saved to {filepath}")

            except requests.exceptions.RequestException as req_err:
                print(f"Error fetching detailed data for {title_name} (UID: {identity}): {req_err}")
            except Exception as e:
                print(f"An unexpected error occurred while processing {title_name} (UID: {identity}): {e}")

    except requests.exceptions.RequestException as req_err:
        print(f"Error fetching data from {endpoint}: {req_err}")
    except Exception as e:
        print(f"An unexpected error occurred while fetching data from {endpoint}: {e}")

# Initialize parameters
date = datetime.now().strftime("%d%m%y%H%M%S")
env = "ENV"
grafana_host = "URL"
api_token = "TOKEN"

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# All directories
main_dir = os.path.dirname(os.path.abspath(__file__))
env_dir = os.path.join(main_dir, f"Grafana_backup/{env}_{date}")
summary_dir = os.path.join(env_dir, "Summary")
alert_dir = os.path.join(env_dir, "grafana_alerts")
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
more_detailed_fetch_and_save(
    endpoint=alert_endpoint, 
    endpoint_dir=alert_dir, 
    uid_key="uid", 
    title_key="title"
)

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
more_detailed_fetch_and_save(
    endpoint=dashboard_detail_endpoint,
    endpoint_dir=dashboard_dir,
    uid_key="uid",
    title_key="title",
    is_folder=True
)

# Fetch and save datasources
fetch_and_save(datasource_endpoint, os.path.join(summary_dir, "datasources.csv"), is_json=False)

# Fetch and save individual datasources
more_detailed_fetch_and_save(
    endpoint=datasource_endpoint,
    endpoint_dir=datasource_dir,
    uid_key="id",
    title_key="name",
    is_folder=False
)

# Summary
print("Backup Summary")
