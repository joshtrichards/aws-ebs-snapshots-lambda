## Overview

This is for managing AWS EC2 EBS volume snapshots. It consists of a snapshot creator and a snapshot manager. 

## Functionality:

- Automatic snapshots (on whatever schedule you prefer)
- Automated expiration of old snapshots
- Ability to configure retention period on a per EC2 instance basis (applying to all volumes attached to said instance)
- Ability to manually tag individual snapshots to be kept indefinitely (regardless of instance retention configuration)
- Does not require a job/management instance; no resources to provision to run snapshot jobs (leverages AWS Lambda)
- Ability to snapshot all Volumes attached to a given Instance (Default), and exclude on a per-Volume basis any indivdual Volume (Through the addition of `Backup = No` Tag to Volume)
- Ability to replicate snapshot to a second AWS Region (As specified by Tag) and remove snapshot from source Region upon successful copy. Tags are replicated from source to destination snapshots

## Tags Configuration

- Instance Level
	- `Backup` { Yes | No }
	- `DestinationRegion` { us-west-1 | eu-west-1 | etc. }
	- `RetentionDays` { 1..x }

- Volume Level
	- `Backup` { Yes | No } (Default if absent = 'Yes') : Overrides default to exclude a given Volume from snapshot

## Implementation Details

It is implemented as a set of two Python based functions intended to run in AWS Lambda (which also handles the job scheduling). This makes it self-contained and easier to setup, without any external resources needed.

Configuration is done through AWS tags. It's easy to configure which instances should have their volumes backed up and how long their snapshots should be retained for. It's also possible to tag certain snapshots for indefinite retention.

The creator function is intended to be ran on a regular basis (i.e. daily), using the built-in AWS Lambda scheduler, to create snapshots for the defined instances/volumes. The manager is also intended to be ran on a regular basis (i.e. also daily, and handles snapshot expiration/retention. 

This is based on code originally posted by Ryan S. Brown in [Scheduling EBS Snapshots - Part I](https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups/) and [Part II](https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups-2/).

For the moment, read these links for documentation on how to setup/use. I've extended it a tiny bit though and need to add docs. :) For hints on changes, see the [CHANGELOG](CHANGELOG.md)

Ideas and To Do items are currently tracked in [IDEAS](IDEAS.md).

## IAM Role

The minimal IAM Role for these Lambda Functions is:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "ec2:DescribeInstances",
                "ec2:DescribeVolumes",
                "ec2:CreateSnapshot",
                "ec2:CreateTags",
                "ec2:CopySnapshot",
                "ec2:DescribeSnapshots",
                "ec2:DeleteSnapshot"
            ],
            "Resource": "*"
        }
    ]
}
```

## Files:

Each file implements a single AWS Lambda function.

- ebs-snapshot-creator.py
- ebs-snapshot-offsiter.py
- ebs-snapshot-manager.py

## Related:

- [AWS auto snapshot script by Joe Richards](https://github.com/viyh/aws-scripts/blob/master/lambda_autosnap.py)
- [AWS EBS Backup Job Run by Lambda by Chris Machler](http://www.evergreenitco.com/evergreenit-blog/2016/4/19/aws-ebs-backup-job-run-by-lambda)
- [DevOps Backup in Amazon EC2](https://medium.com/aws-activate-startup-blog/devops-backup-in-amazon-ec2-190c6fcce41b#.hyo4nyqur)
- [AWS volume snapshots across multiple regions](https://mattyboy.net/general/aws-volume-snapshots-across-multiple-regions/)
- [EBS Snapshots: Crash-Consistent Vs. Application-Consistent](http://www.n2ws.com/blog/ebs-snapshots-crash-consistent-vs-application-consistent.html)
- [N2WS CPM](http://www.n2ws.com/products-services/pricing-registration.html)
- [lambda-expire-snapshots](https://github.com/RideAmigosCorp/lambda-expire-snapshots)
- [Rackspace's Snappy for EBS Snapshots](https://github.com/rackerlabs/ebs_snapper) & (http://blog.rackspace.com/automate-ebs-snapshots-with-snapper)

## Other Relevant Resources (especially if you're going to customize):

- [Boto 3 Docs for EC2](https://boto3.readthedocs.io/en/latest/reference/services/ec2.html)

