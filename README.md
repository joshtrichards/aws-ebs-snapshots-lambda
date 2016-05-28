## Overview

This is for managing AWS EC2 EBS volume snapshots. It consists of a snapshot creator and a snapshot manager. 

It is implemented as a set of two Python based functions intended to run in AWS Lambda (which also handles the job scheduling). This makes it self-contained and easier to setup, without any external resources needed.

Configuration is done through AWS tags. It's easy to configure which instances should have their volumes backed up and how long their snapshots should be retained for. It's also possible to tag certain snapshots for indefinite retention.

The creator function is intended to be ran on a regular basis (i.e. daily), using the built-in AWS Lambda scheduler, to create snapshots for the defined instances/volumes. The manager is also intended to be ran on a regular basis (i.e. also daily, and handles snapshot expiration/retention. 

This is based on code originally posted by Ryan S. Brown in [Scheduling EBS Snapshots - Part I](https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups/) and [Part II](https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups-2/).

For the moment, read these links for documentation on how to setup/use. I've extended it a tiny bit though and need to add docs. :) For hints on changes, see the [CHANGELOG](CHANGELOG.md)

Ideas and To Do items are currently tracked in [IDEAS](IDEAS.md).

## Files:

Each file implements a single AWS Lambda function.

- ebs-snapshot-creator.py
- ebs-snapshot-manager.py

## Functionality:

- automatic snapshots (ran on whatever schedule you prefer)
- automated expiration of old snapshots
- ability to configure retention period on a per instance basis
- ability to manually mark individual snapshots to be kept indefinitely regardless of retention configuration

## Related:

- [AWS auto snapshot script by Joe Richards](https://github.com/viyh/aws-scripts/blob/master/lambda_autosnap.py)
- [AWS EBS Backup Job Run by Lambda by Chris Machler](http://www.evergreenitco.com/evergreenit-blog/2016/4/19/aws-ebs-backup-job-run-by-lambda)

## Other Relevant Resources (especially if you're going to customize):

- [Boto 3 Docs for EC2](https://boto3.readthedocs.io/en/latest/reference/services/ec2.html)

