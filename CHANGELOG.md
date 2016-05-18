
## 0.0.2 - 2016-05-18
### Added
- Second commit based on Ryan S. Brown code that adds support for expiration management
	- https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups-2/
	- instances can be tagged with "Retention" tag so we can define how long to keep snapshots around
	- default Retention period, if none specified, is 7 days
	- snapshots are tagged with DeleteOn that contains the day the snapshot should be deleted. 
	  The date is formatted as YYYY-MM-DD (2015-11-05).
	- new snapshot manager function that handles deletion of old snapshots

## 0.0.1 - 2016-05-18
### Added
- Initial commit based on Ryan S. Brown code
	- Sourced from https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups/
	- simple snapshots
	- *no* support for expiration
