import config_parser
import copy
import boto3
import json


def decorate_body(dict_body, configuration_item):
    new_dict = copy.deepcopy(dict_body)
    new_dict['AlarmName'] = f"{dict_body['AlarmName']}_{configuration_item['resourceId']}"
    new_dict['Dimensions'] = [dict(
        Name="resourceId",
        Value=configuration_item['resourceId']
    )]
    new_dict['Tags'] = [dict(Key="created_by", Value="sentinel")]
    return new_dict


def create_alarms(configuration_item):
    config = config_parser.get_config()
    resource_type = configuration_item["resourceType"]

    if not resource_type in config["resource_types"]:
        raise Exception(f"No alarms defined for resourceType: {resource_type}")

    alarms = config["resource_types"][resource_type]["Alarms"]
    cloudwatch_client = boto3.client('cloudwatch')

    for name, body in alarms.items():
        kwargs = decorate_body(body, configuration_item)
        cloudwatch_client.put_metric_alarm(**kwargs)
