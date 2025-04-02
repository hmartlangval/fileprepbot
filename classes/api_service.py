# import requests

class ApiService:
    def __init__(self, config):
        self.config = config
    
    async def create_pubsub_topics(self, task_id, data):
        if not task_id:
            print("Task ID is not provided. Not Creating Pubsub Topics.")
            return None
        
        try:
            import aiohttp

            server_url = f"{self.config['server_url']}/api/pubsub"
            payload = {
                "id": task_id,
                "data": data
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(server_url, json=payload) as response:
                    if response.status == 200:
                        print(f"Pubsub topic created for task {task_id}.") 
                    else:
                        print(f"Failed to create pubsub topic for task {task_id}. {await response.json()} ")
                
        except Exception as e:
            print(f"Error creating pubsub topic: {e}")
            return None
    
    async def update_extracted_json(self, task_id, extracted_json):
        if not task_id:
            print("Task ID is not provided. Not Updating Extracted JSON to server.")
            return None
        
        try:
            import aiohttp

            server_url = f"{self.config['server_url']}/api/aido-order/{task_id}"
            payload = { 
                "extracted_data": extracted_json
            }

            async with aiohttp.ClientSession() as session:
                async with session.put(server_url, json=payload) as response:
                    if response.status == 200:
                        print(f"Extracted JSON updated for task {task_id}")
                    else:
                        print(f"Failed to update extracted JSON for task {task_id}. {await response.json()}")
        except Exception as e:
            print(f"Error updating extracted JSON: {e}")
            return None

    async def update_task_status(self, task_id, status):
        try:
            import aiohttp

            server_url = f"{self.config['server_url']}/api/aido-order/{task_id}"
            payload = {
                "tax_status": status
            }

            async with aiohttp.ClientSession() as session:
                await session.put(server_url, json=payload)
                print(f"Task status updated to {status}")
              
                if status == "completed":
                    pubsubtype = self.config['pubsub_type']
                    await session.put(f"{self.config['server_url']}/api/pubsub/{pubsubtype}/{task_id}")
                    print(f"Pubsub type {pubsubtype} updated for task {task_id}")
                    
            # do not remove this code, keep this as is for later use.
                # async with session.put(f"{server_url}/{context_id}", json=payload) as response:
                #     if response.status == 200:
                #         print("Configuration updated successfully.")
                #     else:
                #         print(f"Failed to update configuration. Status code: {response.status}")
        except Exception as e:
            print(f"Error updating task status: {e}")
            return None
    
    
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
