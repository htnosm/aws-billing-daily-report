#!/usr/bin/env python
# -*- coding: utf-8 -*-

from boto3.session import Session
from datetime import datetime, timedelta, timezone
from operator import itemgetter
import textwrap
import os
import slackweb

Namespace = "AWS/Billing"
MetricName = "EstimatedCharges"


def post_slack(message):
    SlackWebhookURL = os.environ['SlackWebhookURL']
    SlackChannel = os.environ['SlackChannel']
    SlackUsername = os.environ['SlackUsername']
    SlackIconEmoji = os.environ['SlackIconEmoji']
    SlackColor = os.environ['SlackColor']
    SlackTitle = os.environ['SlackTitle']

    slack = slackweb.Slack(url=SlackWebhookURL)
    attachments = [{
        'title': SlackTitle,
        'text': message,
        'color': SlackColor,
    }]
    response = slack.notify(
        channel=SlackChannel,
        username=SlackUsername,
        icon_emoji=SlackIconEmoji,
        attachments=attachments,
    )
    return response


def cw_get_metric_data_diff(client, dimensions, start_time, end_time, period=86400, stat='Maximum'):
    response = client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'string',
                'MetricStat': {
                    'Metric': {
                        'Namespace': Namespace,
                        'MetricName': MetricName,
                        'Dimensions': dimensions
                    },
                    'Period': period,
                    'Stat': stat,
                },
                'ReturnData': True,
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
        ScanBy='TimestampAscending',
    )

    data = response['MetricDataResults'][0]
    bef = data['Values'][0]
    aft = data['Values'][1]
    diff = round(data['Values'][1] - data['Values'][0], 2)
    if diff < 0:
        diff = "-"

    return {
        'bef': bef,
        'aft': aft,
        'diff': diff,
    }


def cw_list_metrics(client):
    response = client.list_metrics(
        Namespace=Namespace,
        MetricName=MetricName,
        Dimensions=[
            {
                'Name': 'Currency',
                'Value': 'USD'
            },
        ],
    )
    return response['Metrics']


def format_message(time_range, total, details):
    headers = ["ServiceName", "Prev", "Now", "Diff"]
    header = "| " + " | ".join(headers) + " |"
    table_separate = ("| --- " * len(headers)) + "|"
    total_rows = "| " + " | ".join([str(v) for v in total.values()]) + " |"
    rows = []
    for detail in details:
        row = "| " + " | ".join([str(v) for v in detail.values()]) + " |"
        rows.append(row)
    detail_rows = "\n".join(rows)

    message = textwrap.dedent('''
```
* {time_range}

# Total

{header}
{table_separate}
{total_rows}

## Details

{header}
{table_separate}
{detail_rows}
```
''').format(
        time_range=time_range,
        header=header,
        table_separate=table_separate,
        total_rows=total_rows,
        detail_rows=detail_rows,
    )
    return message


def lambda_handler(event, context):
    session = Session(region_name="us-east-1")
    cw = session.client('cloudwatch')
    until = datetime.now(timezone.utc)
    since = until - timedelta(days=2)
    until_str = until.strftime("%Y/%m/%d %H:%M:%S %Z")
    since_str = since.strftime("%Y/%m/%d %H:%M:%S %Z")
    time_range = f"{since_str} - {until_str}"

    total = ''
    details = []
    for metric in cw_list_metrics(cw):
        dimensions = metric['Dimensions']
        row = {'service': 'Total'}
        for dimension in dimensions:
            if dimension['Name'] == 'ServiceName':
                row['service'] = dimension['Value']

        response = cw_get_metric_data_diff(cw, dimensions, since, until)
        row.update(response)

        if row['service'] == "Total":
            total = row
        else:
            if row['bef'] + row['aft'] > 0:
                details.append(row)

    details_sorted = sorted(details, key=itemgetter('diff'), reverse=True)
    message = format_message(time_range, total, details_sorted)
    print(f"message: {message}")
    response = post_slack(message)
    print(f"response: {response}")


if __name__ == '__main__':
    lambda_handler(None, None)
