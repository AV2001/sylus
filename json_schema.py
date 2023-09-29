import os
import openai
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

outlook_custom_functions = [
    {
        'name': 'sending_email_info',
        'description': 'Use when sending an email.',
        'parameters': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'Name of the person the email is being sent to.'
                },
                'to_address': {
                    'type': 'string',
                    'description': 'Email address of the person the email is being sent to.'
                },
                'subject': {
                    'type': 'string',
                    'description': 'Subject of the email.'
                },
                'body': {
                    'type': 'string',
                    'description': 'The content the user likes to talk about in the email. This must follow proper email structure in HTML tags.'
                }
            },
            'required': ['name', 'subject', 'body']
        }
    },
    {
        'name': 'reading_email_info',
        'description': 'Use when reading an email.',
        'parameters': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'Name of the person.'
                },
                'intent': {
                    'type': 'string',
                    'description': 'Whether the user likes to "send" or "read" the email.'
                }
            }
        }
    }
]


def get_completion(prompt):
    '''Send an email via Outlook.'''
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo-0613',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.7,
        functions=outlook_custom_functions,
        function_call='auto'
    )

    # Load the response as a json object
    total_tokens = response['usage']['total_tokens']
    print(f'TOTAL TOKENS: {total_tokens}')
    json_response = response['choices'][0]['message']
    function_name, arguments = json_response['function_call']['name'], json.loads(
        json_response['function_call']['arguments'])

    return (function_name, arguments)
