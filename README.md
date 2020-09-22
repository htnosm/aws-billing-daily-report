# aws-billing-daily-report
AWS Billing EstimatedCharges Daily Report

## Description

Use CloudWatch Metrics **Billing** data to notify Slack.  
Must be enabled the monitoring of estimated charges for your AWS account.


## Requirements

* [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* python 3.8+
* [slackweb · PyPI](https://pypi.org/project/slackweb/)

## Installation

```
sam build
sam deploy --guided
```

* Configuring SAM deploy

```
	Setting default arguments for 'sam deploy'
	=========================================
	Stack Name [sam-app]: aws-billing-daily-report
	AWS Region [us-east-1]:
	Parameter SlackWebhookURL []: https://hooks.slack.com/services/xxx/xxx
	Parameter SlackChannel []: your-slack-channel
	Parameter SlackUsername [aws-billing-daily-report]:
	Parameter SlackIconEmoji [:money_with_wings:]:
	Parameter SlackColor [#008000]:
	Parameter SlackTitle [EstimatedCharges DailyReport]:
	#Shows you resources changes to be deployed and require a 'Y' to initiate deploy
	Confirm changes before deploy [y/N]: y
	#SAM needs permission to be able to create roles to connect to the resources in your template
	Allow SAM CLI IAM role creation [Y/n]: y
	Save arguments to samconfig.toml [Y/n]: y
```

## Notification example

```
EstimatedCharges DailyReport

* yyyy/mm/dd hh:mm:ss UTC - yyyy/mm/dd hh:mm:ss UTC

# Total

| ServiceName | Prev | Now | Diff |
| --- | --- | --- | --- |
| Total | 0.00 | 0.00 | 0.00 |

## Details

| ServiceName | Prev | Now | Diff |
| --- | --- | --- | --- |
| AmazonEC2 | 0.00 | 0.00 | 0.00 |
| AmazonCloudWatch | 0.00 | 0.00 | 0.00 |
| AmazonVPC | 0.00 | 0.00 | 0.00 |
```
