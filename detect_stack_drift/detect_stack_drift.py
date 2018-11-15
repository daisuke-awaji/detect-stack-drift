import json

import boto3

client = boto3.client('cloudformation')

from datetime import date, datetime

def json_serial(obj):
    """date, datetime conversion function
    """
    # For date type, convert it to a character string
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    # Not supported except above
    raise TypeError ("Type %s not serializable" % type(obj))

def json_dumps(obj):
    """json serializable function (for debug)
    """
    return json.dumps(obj, default=json_serial, indent=4, separators=(',', ': '))

def success_response(msg):
    return {
        "statusCode": 200,
        "body": json.dumps({
            'message': msg
        })
    }

def lambda_handler(event, context):

    token = ''
    modified_flag = False
    while token is not None:
        response = client.describe_stacks() if token == '' else client.describe_stacks(NextToken=token)
        token = response['NextToken'] if 'NextToken' in response else None
        for stack in response['Stacks']:
            client.detect_stack_drift(StackName=stack['StackName'])
            for stack_resource_drift in client.describe_stack_resource_drifts(StackName=stack['StackName'])['StackResourceDrifts']:
                if stack_resource_drift['StackResourceDriftStatus'] != 'IN_SYNC':
                    print(stack_resource_drift['StackId'], stack_resource_drift['StackResourceDriftStatus'])
                    modified_flag = True

    error = '[ERROR] Stack is manually operated from the AWS console. Check the status of the current stack.'
    success = '[SUCCESS] All Stacks have not been manually changed from the AWS console.'
    return success_response(msg=(error if modified_flag else success))
