Based on:
	- Code from Ryan S. Brown
		- https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups/
		- https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups-2/

Related:

	- https://github.com/viyh/aws-scripts/blob/master/lambda_autosnap.py
	- http://www.evergreenitco.com/evergreenit-blog/2016/4/19/aws-ebs-backup-job-run-by-lambda

Files:

	- ebs-snapshot-creator.py

Functionality:

	- simple snapshots
	- expiration of old snapshots
	- configuration of retention period on a per instance basis
	- ability to manually tag select snapshots to be kept indefinitely regardless of retention configuration
