import os
import requests


async def extract_message_data(self, message):
    json_data = self.extract_json_data(message)
    if json_data:
        s_data = json_data.get('s_data', {})
    else:
        s_data = {}
    return [json_data, s_data]


async def format_output(script_executor, v2_config, result):
    formatter = v2_config.get('output_template_function', None)
    if formatter:
        [file_name, function_name] = formatter.split(':')
        script_executor.SessionData['result'] = result
        return await script_executor.execute(file_name.strip(), function_name.strip())
    
    return f"Action {v2_config.get('name', 'unknown')} result: {result}"


def create_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

async def get_aido_order(id):
    url = f"http://localhost:3000/api/aido-order/{id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json() or {}
        record = data.get('record', {})
        return record
    else:
        raise Exception(f"Failed to get AIDO order for id: {id}, status code: {response.status_code}")

async def update_downloads_folder(id, folderPath: str):
    url = f"http://localhost:3000/api/dynamic/aido_order_processing/{id}"
    response = requests.put(url, data={'downloads_folder': folderPath})
    # response.raise_for_status()
    # data = response.json() or None
    # record = data.get('record', {})
    # return record

async def ensure_downloads_folder(self, database_id, order_number):
    print("trying to ensure downloads folder")
    if database_id is None or order_number is None:
        raise Exception("Database ID or Order Number is None")

    existing_folder = ""
    if database_id:
        print("id for the request:", database_id)
        record = await get_aido_order(database_id)
        existing_folder = record.get('downloads_folder', None)
        print('existing folder:', existing_folder)
    
    if existing_folder:
        create_if_not_exists(existing_folder)
        return existing_folder;
    else:
        # self.config['custom_downloads_path'] = new_dl_folder
        # new_dl_folder = create_download_folder(default_dl_path, order_number)
        new_dl_folder = self.create_custom_downloads_directory(order_number)
        if new_dl_folder is None:
            raise Exception("New Downloads Folder is None")
        
        await update_downloads_folder(database_id, new_dl_folder)
        return new_dl_folder
