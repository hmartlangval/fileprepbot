import sys
sys.path.insert(0, r"D:\cursor\base_bot\aido-base-bot")


import os
import json
import threading
import time
import uuid
from bottle import Bottle, request, response, static_file, run
from dotenv import load_dotenv
from base_bot import BaseBot
from abstract_task_bot import AbstractTaskBot
# Load environment variables
load_dotenv()

# Bot data structures
active_bots = {}
bot_instances = {}  # To store actual bot instances
bot_instances_types = {
    "base": {
        "id": "base",
        "name": "Base Bot",
        "description": "A basic bot with messaging capabilities",
        "configurable": False,
        "instance": BaseBot
    },
    "browser": {
        "id": "browser",
        "name": "Browser Bot",
        "description": "A browser bot with browsing capabilities",
        "configurable": True,
        "instance": AbstractTaskBot
    },
}

# Create Bottle app
app = Bottle()

# Enable CORS for the API
@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@app.route('/options', method=['OPTIONS'])
def options_handler():
    return {}

# Static files
@app.route('/')
def index():
    return static_file('index.html', root='static')

@app.route('/api-docs.html')
def api_docs():
    return static_file('api-docs.html', root='static')

@app.route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='static')

# API Routes
@app.route('/api/bots', method='GET')
def get_all_bots():
    return {"bots": list(active_bots.values())}

@app.route('/api/bot-instance-types', method='GET')
def get_bot_instances():
    # Return the bot_types dictionary values as a list
    serializable_types = [
        {
            "id": bot_bases["id"],
            "name": bot_bases["name"], 
            "description": bot_bases["description"],
            "configurable": bot_bases["configurable"]
        }
        for bot_bases in bot_instances_types.values()
    ]
    return {"botInstanceTypes": serializable_types}

@app.route('/api/bots', method='POST')
def create_bot():
    try:
        data = request.json
        
        if not data:
            response.status = 400
            return {"error": "Invalid request format"}
        
        bot_id = data.get('botId') or str(uuid.uuid4())
        bot_instance_type = data.get('botInstanceType', 'base')
        bot_name = data.get('botName', 'Unnamed Bot')
        # channel = data.get('channel', 'general')
        
        # options = data.get('options', {})
        # options['model'] = 'gpt-4o-mini'
        # options['prompts_directory'] = os.getenv("PROMPTS_DIR_PATH", "prompts")
        
        # options = data.get('options', {})
        # options['model'] = 'gpt-4o-mini'
        # options['prompts_directory'] = os.getenv("PROMPTS_DIR_PATH", "prompts")
        
        
        if bot_id in active_bots:
            response.status = 409
            return {"error": f"Bot with ID {bot_id} already exists"}
        
        if bot_instance_type not in bot_instances_types:
            response.status = 400
            return {"error": f"Invalid bot type: {bot_instance_type}"}
      
        # just so we don't accept 100% input, we are doing one more JSON creation
        config_json = {
            "botId": bot_id,
            "botName": bot_name,
            "channel": data.get('channel', 'general'),
            "botInstanceType": bot_instance_type,
            "botType": "task_bot",
            "status": "active",
            "autojoin_channel": data.get('channel', 'general'),
            "options": data.get('options', {}),
            "createdAt": time.time()
        }
        config_json["options"]["model"] = 'gpt-4o-mini'
        config_json["options"]["prompts_directory"] = os.getenv("PROMPTS_DIR_PATH", "prompts")
        # # Create bot instance (now using actual BaseBot class)
        # options_dict = {
        #     "botId": bot_id,
        #     "botName": bot_name,
        #     "channel": channel,
        #     "botInstanceType": bot_instance_type,
        #     "botType": "task_bot",
        #     "options": options,
        # }
        
        # Add any other custom options
        # if options:
        #     for key, value in options.items():
        #         options_dict[key] = value
        
        # Create the actual bot instance
        bot_instance = create_actual_bot(bot_instance_type, config_json)
        
        if not bot_instance:
            response.status = 500
            return {"error": f"Failed to create bot of type {bot_instance_type}"}
        
        # Store the bot instance
        # bot_instances[bot_id] = bot_instance
        
        # Create the bot record
        # new_bot = {
        #     "botId": bot_id,
        #     "botName": bot_name,
        #     "channel": channel,
        #     "botInstanceType": bot_instance_type,
        #     "botType": bot_type,
        #     "status": "active",
        #     "autojoin_channel": autojoin_channel,
        #     "options": options,
        #     "createdAt": time.time()
        # }
        
        # active_bots[bot_id] = bot_instance
        
        # print(f"Created bot: {bot_name} ({bot_id}) of type {bot_instance_type}")
        
        # # Start the bot
        # bot_instance.start()
        
        return {"success": True, "bot": data}
    
    except Exception as e:
        response.status = 500
        return {"error": str(e)}

@app.route('/api/bots/<bot_id>', method='DELETE')
def stop_bot(bot_id):
    if bot_id not in active_bots:
        response.status = 404
        return {"error": f"Bot with ID {bot_id} not found"}
    
    # Stop the actual bot instance if it exists
    if bot_id in bot_instances:
        try:
            bot_instance = bot_instances[bot_id]
            bot_instance.stop()
            del bot_instances[bot_id]
            print(f"Stopped bot instance: {bot_id}")
        except Exception as e:
            print(f"Error stopping bot instance {bot_id}: {str(e)}")
    
    # Remove from active bots list
    bot = active_bots.pop(bot_id)
    print(f"Stopped bot: {bot['botName']} ({bot_id})")
    
    return {"success": True, "botId": bot_id}

@app.route('/api/bots', method='DELETE')
def stop_all_bots():
    bot_count = len(active_bots)
    
    if bot_count == 0:
        return {"success": True, "message": "No active bots to stop"}
    
    # Stop all actual bot instances
    for bot_id, bot_instance in list(bot_instances.items()):
        try:
            bot_instance.stop()
            print(f"Stopped bot instance: {bot_id}")
        except Exception as e:
            print(f"Error stopping bot instance {bot_id}: {str(e)}")
    
    # Clear bot instances
    bot_instances.clear()
    
    # Get the list of stopped bots before clearing
    bots_stopped = list(active_bots.keys())
    
    # Clear the active bots list
    active_bots.clear()
    
    print(f"Stopped all bots ({bot_count})")
    
    return {"success": True, "botsStoppedCount": bot_count, "botsIds": bots_stopped}

@app.route('/api/bots/<bot_id>/command', method='POST')
def send_command(bot_id):
    if bot_id not in active_bots:
        response.status = 404
        return {"error": f"Bot with ID {bot_id} not found"}
    
    data = request.json
    
    if not data:
        response.status = 400
        return {"error": "Invalid request format"}
    
    command = data.get('command')
    
    if not command:
        response.status = 400
        return {"error": "Command is required"}
    
    # Send command to the actual bot instance if it exists
    if bot_id in bot_instances:
        try:
            bot_instance = bot_instances[bot_id]
            success = bot_instance.add_command(command)
            if success:
                print(f"Sent command '{command}' to bot {bot_id}")
                return {"success": True, "botId": bot_id, "command": command}
            else:
                response.status = 500
                return {"error": f"Bot {bot_id} is not running"}
        except Exception as e:
            response.status = 500
            return {"error": f"Error sending command to bot {bot_id}: {str(e)}"}
    else:
        # Simulated command handling if no actual instance
        print(f"Simulated command '{command}' to bot {bot_id}")
        return {"success": True, "botId": bot_id, "command": command}

# Add new endpoint to get a single bot by ID
@app.route('/api/bots/<bot_id>', method='GET')
def get_bot_by_id(bot_id):
    if bot_id not in active_bots:
        response.status = 404
        return {"error": f"Bot with ID {bot_id} not found"}
    
    return {"success": True, "bot": active_bots[bot_id]}

# Add new endpoint to restart a bot
@app.route('/api/bots/<bot_id>/restart', method='POST')
def restart_bot(bot_id):
    if bot_id not in active_bots:
        response.status = 404
        return {"error": f"Bot with ID {bot_id} not found"}
    
    # Save the current bot configuration
    bot_config = active_bots[bot_id]
    
    # Stop the bot instance if it exists
    if bot_id in bot_instances:
        try:
            bot_instance = bot_instances[bot_id]
            bot_instance.stop()
            del bot_instances[bot_id]
            print(f"Stopped bot instance: {bot_id} for restart")
        except Exception as e:
            print(f"Error stopping bot instance {bot_id}: {str(e)}")
    
    # Remove from active bots list temporarily
    active_bots.pop(bot_id)
    
    # Create a new instance using the same configuration
    bot_instance = create_actual_bot(bot_config["botInstanceType"], bot_config)
    
    if not bot_instance:
        response.status = 500
        return {"error": f"Failed to restart bot of type {bot_config['botInstanceType']}"}
    
    print(f"Restarted bot: {bot_config['botName']} ({bot_id})")
    
    return {"success": True, "botId": bot_id, "message": f"Bot {bot_id} restarted successfully"}

# Function to create the actual bot instance based on type
def create_actual_bot(bot_instance_type, config_json):
    
    opt_dict = option_json_to_dict(options_json=config_json)
    opt_dict["disable_console_input"] = True
    
    try:
        bot_id = opt_dict.get('bot_id', '')
        bot_instance = bot_instances_types[bot_instance_type]["instance"](opt_dict)
        
        if bot_instance:
            # Store the bot instance
            bot_instances[bot_id] = bot_instance
            active_bots[bot_id] = config_json
            
            # Add to active bots list
            # active_bots[bot_id] = {
            #     "botId": bot_id,
            #     "botName": config_json["botName"],
            #     "channel": config_json["channel"], 
            #     "botInstanceType": config_json["botInstanceType"],
            #     "botType": config_json["botType"],
            #     "options": config_json["options"],
            #     "status": "active",
            #     "createdAt": time.time()
            # }
            
            
            # Start the bot
            bot_instance.start()
            
            print(f"Created demo bot: {config_json['botName']} ({bot_id})")
        # For now, just create a BaseBot instance
        # In a more complete implementation, you would create different types of bots here
        # bot_instance = BaseBot(options)
        return bot_instance
    except Exception as e:
        print(f"Error creating bot instance: {str(e)}")
        return None

# Console commands handling
def handle_console_commands():
    print("=== Bot Management Console ===")
    print("Commands: create, stop, stopall, list, send, exit")
    
    while True:
        try:
            cmd_input = input("\nCommand > ").strip()
            
            if not cmd_input:
                continue
            
            cmd_parts = cmd_input.split()
            cmd = cmd_parts[0].lower()
            
            if cmd == 'exit':
                print("Exiting application...")
                # Stop all bots before exiting
                for bot_id, bot_instance in list(bot_instances.items()):
                    try:
                        bot_instance.stop()
                        print(f"Stopped bot instance: {bot_id}")
                    except:
                        pass
                os._exit(0)
                
            elif cmd == 'list':
                if not active_bots:
                    print("No active bots")
                else:
                    print(f"\nActive Bots ({len(active_bots)}):")
                    for bot_id, bot in active_bots.items():
                        print(f"- {bot['botName']} ({bot_id}) [Type: {bot['botType']}] [Channel: {bot['channel']}]")
                
            elif cmd == 'create':
                if len(cmd_parts) < 2:
                    print("Usage: create [bot_id] [bot_name] [channel] [type] [options]")
                    continue
                
                bot_id = cmd_parts[1]
                bot_name = cmd_parts[2] if len(cmd_parts) > 2 else f"Bot {bot_id}"
                channel = cmd_parts[3] if len(cmd_parts) > 3 else "general"
                bot_instance_type = cmd_parts[4] if len(cmd_parts) > 4 else "base"
                
                if bot_id in active_bots:
                    print(f"Bot with ID {bot_id} already exists")
                    continue
                
                if bot_instance_type not in bot_instances_types:
                    print(f"Invalid bot type: {bot_instance_type}")
                    continue
                
                # # Create the bot instance using the same function as the API
                # options_dict = {
                #     "bot_id": bot_id,
                #     "bot_name": bot_name,
                #     "bot_instance_type": bot_instance_type,
                #     "bot_type": "task_bot",
                #     "autojoin_channel": channel
                # }
                config_json = {
                    "botId": bot_id,
                    "botName": bot_name,
                    "botInstanceType": bot_instance_type,
                    "botType": "task_bot",
                    "channel": channel,
                    "autoJoinChannel": channel
                }
                
                # Create the actual bot instance
                bot_instance = create_actual_bot(bot_instance_type, config_json)
                
                if not bot_instance:
                    print(f"Failed to create bot of type {bot_instance_type}")
                    continue
                
                # # Store the bot instance
                # bot_instances[bot_id] = bot_instance
                
                # # Create the bot record
                # new_bot = {
                #     "botId": bot_id,
                #     "botName": bot_name,
                #     "channel": channel,
                #     "botInstanceType": bot_instance_type,
                #     "botType": "task_bot",
                #     "status": "active",
                #     "options": {},
                #     "createdAt": time.time()
                # }
                
                # active_bots[bot_id] = new_bot
                
                # # Start the bot
                # bot_instance.start()
                
                # print(f"Created bot: {bot_name} ({bot_id}) of type {bot_instance_type}")
                
            elif cmd == 'stop':
                if len(cmd_parts) < 2:
                    print("Usage: stop [bot_id]")
                    continue
                
                bot_id = cmd_parts[1]
                
                if bot_id not in active_bots:
                    print(f"Bot with ID {bot_id} not found")
                    continue
                
                # Stop the actual bot instance if it exists
                if bot_id in bot_instances:
                    try:
                        bot_instance = bot_instances[bot_id]
                        bot_instance.stop()
                        del bot_instances[bot_id]
                        print(f"Stopped bot instance: {bot_id}")
                    except Exception as e:
                        print(f"Error stopping bot instance {bot_id}: {str(e)}")
                
                # Remove from active bots list
                bot = active_bots.pop(bot_id)
                print(f"Stopped bot: {bot['botName']} ({bot_id})")
                
            elif cmd == 'stopall':
                bot_count = len(active_bots)
                
                if bot_count == 0:
                    print("No active bots to stop")
                    continue
                
                # Stop all actual bot instances
                for bot_id, bot_instance in list(bot_instances.items()):
                    try:
                        bot_instance.stop()
                        print(f"Stopped bot instance: {bot_id}")
                    except Exception as e:
                        print(f"Error stopping bot instance {bot_id}: {str(e)}")
                
                # Clear bot instances and active bots
                bot_instances.clear()
                active_bots.clear()
                
                print(f"Stopped all bots ({bot_count})")
                
            elif cmd == 'send':
                if len(cmd_parts) < 3:
                    print("Usage: send [bot_id] [command]")
                    continue
                
                bot_id = cmd_parts[1]
                command = ' '.join(cmd_parts[2:])
                
                if bot_id not in active_bots:
                    print(f"Bot with ID {bot_id} not found")
                    continue
                
                # Send command to the actual bot instance if it exists
                if bot_id in bot_instances:
                    try:
                        bot_instance = bot_instances[bot_id]
                        success = bot_instance.add_command(command)
                        if success:
                            print(f"Sent command '{command}' to bot {bot_id}")
                        else:
                            print(f"Failed to send command: Bot {bot_id} is not running")
                    except Exception as e:
                        print(f"Error sending command to bot {bot_id}: {str(e)}")
                else:
                    # Simulated command handling if no actual instance
                    print(f"Simulated command '{command}' to bot {bot_id}")
                
            else:
                print(f"Unknown command: {cmd}")
                print("Available commands: create, stop, stopall, list, send, exit")
        
        except KeyboardInterrupt:
            print("\nExiting application...")
            # Stop all bots before exiting
            for bot_id, bot_instance in list(bot_instances.items()):
                try:
                    bot_instance.stop()
                except:
                    pass
            os._exit(0)
            
        except Exception as e:
            print(f"Error: {str(e)}")

def option_json_to_dict(options_json): 
    
    bot_id = options_json["botId"]
    options_dict = {
        "bot_id": bot_id,
        "bot_name": options_json["botName"],
        "bot_instance_type": options_json["botInstanceType"],
        "bot_type": options_json["botType"],
        "autojoin_channel": options_json["autoJoinChannel"] if "autoJoinChannel" in options_json else options_json["channel"]
    }
    
    # Add any other custom options
    if options_json["options"]:
        for key, value in options_json["options"].items():
            options_dict[key] = value
    
    return options_dict
    
def create_demo_bot():
    demo_bots = [
        {
            "botId": "taxbot",
            "botName": "TaxBot",
            "channel": "general",
            "botInstanceType": "browser",
            "botType": "task_bot",            
            "options": {
                "model": "gpt-4o-mini",
                "prompts_directory": os.getenv("PROMPTS_DIR_PATH", "prompts"),
            }
        },
        # {
        #     "botId": "d2",
        #     "botName": "Demo Bot 2",
        #     "channel": "general",
        #     "botType": "base",
        #     "options": {},
        #     "instance": BaseBot
        # }
    ]
    
    # Create and start demo bots
    for demo_bot in demo_bots:
        create_actual_bot(demo_bot["botInstanceType"], demo_bot)
        
        
       
    
# Main function
def main():
    # Create demo bots
    # create_demo_bot()
    
    # Start the console commands thread
    console_thread = threading.Thread(target=handle_console_commands)
    console_thread.daemon = True
    console_thread.start()
    
    # Start the Bottle server
    host = os.environ.get('HOST', 'localhost')
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting server on http://{host}:{port}")
    print("Press Ctrl+C to exit")
    
    try:
        # Run the server with a more reliable server if available
        run(app, host=host, port=port, server='auto', reloader=False)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        # Stop all bots when the server stops
        print("Stopping all bots...")
        for bot_id, bot_instance in list(bot_instances.items()):
            try:
                bot_instance.stop()
                print(f"Stopped bot instance: {bot_id}")
            except:
                pass

if __name__ == '__main__':
    main() 