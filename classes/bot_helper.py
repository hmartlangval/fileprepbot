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