# Based on:

- Code from Ryan S. Brown
  - https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups/
  - https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups-2/

(read the above links for documentation on how to setup/use for the time being)

# Related:

- https://github.com/viyh/aws-scripts/blob/master/lambda_autosnap.py
- http://www.evergreenitco.com/evergreenit-blog/2016/4/19/aws-ebs-backup-job-run-by-lambda

# Files:

Each file implements a single AWS Lambda function.

- ebs-snapshot-creator.py
- ebs-snapshot-manager.py

# Functionality:

- automatic snapshots (ran on whatever schedule you prefer)
- automated expiration of old snapshots
- ability to configure retention period on a per instance basis
- ability to manually mark individual snapshots to be kept indefinitely regardless of retention configuration
