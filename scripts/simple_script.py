async def simple_script(self, context):
    session_data = context.SessionData
    # print(session_data)
    # session_data['instructions'] = 'test this is  new instruction customized for this script'
    # context.SessionData = session_data
    return

async def output_template_mainbot(self, context):
    result = context.SessionData['result']
    return f"Formatted response: {result}"
