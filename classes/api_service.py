# import requests

class ApiService:
    def __init__(self, config):
        self.config = config
    
    async def create_new_task(self, ref_id, queue_id):
        if not ref_id:
            raise Exception('Failed to create a referenc ID for task queue.')
        
        try:
            import aiohttp

            server_url = f"{self.config['server_url']}/api/dynamic/tasks"
            payload = {
                "refId": ref_id,
                "status": "queued",
                "queue": queue_id
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(server_url, json=payload) as response:
                    if response.status == 200:
                        print(f"Task add to queue {queue_id} with refId: {ref_id}.") 
                    else:
                        print(f"Failed to create task for queue {queue_id} for refId: {ref_id}. {await response.json()} ")
                
        except Exception as e:
            print(f"Error creating task for queue: {e}")
            raise e
    
    async def update_aido_extracted_json(self, aido_order_id, extracted_json, downloads_path=None):
        if not aido_order_id:
            print("AIDO Order ID is not provided. Not Updating Extracted JSON to server.")
            return None
        
        try:
            import aiohttp

            server_url = f"{self.config['server_url']}/api/dynamic/aido_order_processing/{aido_order_id}"
            payload = { 
                "extracted_data": extracted_json,
                "downloads_path": downloads_path
            }

            async with aiohttp.ClientSession() as session:
                async with session.put(server_url, json=payload) as response:
                    if response.status == 200:
                        print(f"Extracted JSON updated for AIDO Order {aido_order_id}")
                    else:
                        print(f"Failed to update extracted JSON for Order {aido_order_id}. {await response.json()}")
        except Exception as e:
            print(f"Error updating extracted JSON: {e}")
            return None

    # async def update_task_status(self, task_id, status):
    #     try:
    #         import aiohttp

    #         server_url = f"{self.config['server_url']}/api/aido-order/{task_id}"
    #         payload = {
    #             "tax_status": status
    #         }

    #         async with aiohttp.ClientSession() as session:
    #             await session.put(server_url, json=payload)
    #             print(f"Task status updated to {status}")
              
    #             if status == "completed":
    #                 pubsubtype = self.config['pubsub_type']
    #                 await session.put(f"{self.config['server_url']}/api/pubsub/{pubsubtype}/{task_id}")
    #                 print(f"Pubsub type {pubsubtype} updated for task {task_id}")
                    
    #         # do not remove this code, keep this as is for later use.
    #             # async with session.put(f"{server_url}/{context_id}", json=payload) as response:
    #             #     if response.status == 200:
    #             #         print("Configuration updated successfully.")
    #             #     else:
    #             #         print(f"Failed to update configuration. Status code: {response.status}")
    #     except Exception as e:
    #         print(f"Error updating task status: {e}")
    #         return None
    
    
    # def update_task_status2(self, task_id, status):
    #     try:
    #         url = f"{self.config['server_url']}/api/aido-order/{task_id}"
    #         payload = {
    #             "status": status
    #         }
    #         response = requests.put(url, json=payload)
    #         return response.json()
    #     except Exception as e:
    #         print(f"Error updating task status: {e}")
    #         return None
