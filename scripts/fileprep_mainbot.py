import json

async def format_output(self, context):
    
    json_result = context.SessionData['result']
    
    # @taxbot @propertybot New task assigned for order: {userInput_json.get('order_number', 'n/a')} [json]{json.dumps(userInput_json)}[/json]"
    json_result['x_county'] = json_result.get("s_data", {}).get('x_county', None)
    return f"@taxbot @propertybot New task assigned for order: {json_result.get('order_number', 'n/a')} [json]{json.dumps(json_result)}[/json]"