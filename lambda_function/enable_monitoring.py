import boto3
import logging
import config_parser
from create_alarms import create_alarms

# config
config = config_parser.get_config()


# Iterate through required tags ensureing each required tag is present,
# and value is one of the given valid values
def if_monitoring_enabled(configuration_item):
    current_tags = configuration_item["configuration"].get("tags", [])
    monitoring_enabled = False
    for tag in current_tags:
        if tag["key"] == config["monitoring_enabled_tag"]["Key"] \
                and tag["value"] == config["monitoring_enabled_tag"]["Value"]:
            monitoring_enabled = True
    return monitoring_enabled


def tag_resource(resource_arn):
    client = boto3.client('resourcegroupstaggingapi')
    client.tag_resources(
        ResourceARNList=[resource_arn],
        Tags={
            config["monitoring_enabled_tag"]["Key"]: config["monitoring_enabled_tag"]["Value"]
        }
    )


def enable_monitoring(configuration_item):
    if configuration_item["resourceType"] not in config["resource_types"]:
        return {
            "compliance_type": "NOT_APPLICABLE",
            "annotation": "The rule doesn't apply to resources of type " +
                          configuration_item["resourceType"] + "."
        }

    if configuration_item["configurationItemStatus"] == "ResourceDeleted":
        return {
            "compliance_type": "NOT_APPLICABLE",
            "annotation": "The configurationItem was deleted and therefore cannot be validated."
        }

    if if_monitoring_enabled(configuration_item):
        return {
            "compliance_type": "COMPLIANT",
            "annotation": "Monitoring is already enabled for this resource"
        }
    try:
        create_alarms(configuration_item)
        tag_resource(configuration_item['ARN'])
    except Exception as e:
        logging.exception("Error occured while setting up monitoring: %s" % e)
        return {
            "compliance_type": "NON_COMPLIANT",
            "annotation": "Error occured while setting up monitoring: %s" % e
        }
    else:
        return {
            "compliance_type": "COMPLIANT",
            "annotation": "Monitoring is already enabled for this resource"
        }

