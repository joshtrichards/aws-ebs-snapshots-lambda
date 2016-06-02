## ebs-snapshot-creator.py

- The device name on instance that the snapshotted volume was attached to at time of snapshot job run should be included in the snapshot Description
  - Add during snapshot instance volume device name tracking to snapshot creator?

- Get notified when Lambda function emits an error - e.g. http://docs.aws.amazon.com/lambda/latest/dg/with-scheduledevents-example.html

- It should be possible to configure and create out-of-region snapshots without external tools (will require addition of support in manager for retention)

- Trigger a optional (if configured) web hook every time it runs (e.g. to use with PagerDuty to trigger if job doesn't check-in every N days/hours/whatever)
- Add JSON for IAM and/or CloudFormation and/or Terraform code for deploying

## ebs-snapshot-manager.py

- Add support for retention of most recent X weeks to manager 
  - versus current only most recent X days support
  - to permit one-day-a-week going back X weeks snapshot retention/archiving support
- Add support for retention of most recent X months to manager
  - versus current only most recent X days support
  - to permit one-day-a-month going back X months snapshot retention/archiving support
- manager out-of-region snapshots too
- Trigger a optional (if configured) web hook every time it runs (e.g. to use with PagerDuty to trigger if job doesn't check-in every N days/hours/whatever)
- Get notified when Lambda function emits an error - e.g. http://docs.aws.amazon.com/lambda/latest/dg/with-scheduledevents-example.html
- Add JSON for IAM and/or CloudFormation and/or Terraform code for deploying

## ebs-snapshot-watcher.py

- Find the volume(s) without snapshot(s) and, unless tagged for being ignored, notify about them
- There should be detection of snapshot failures and easier alerting
  - Investigate failure scenarios for snapshot creator
  - Investigate how to improve notification/alerting on failure for snapshot creator
  - Thoughts:
    - due to design maybe either adding watchdog code to the manager when it sees configured instances not getting backed up to alert
    - or in the interest of modularity, creating a watchdog/alert/monitor function/job that looks for indications of problems (starting
      with configured instances not being recently backed up, obvious indictations of snapshot jobs failing in logs, expired snapshots 
      not being cleared, etc.)
- Watch out-of-region snapshots too
- Trigger a optional (if configured) web hook every time it runs (e.g. to use with PagerDuty to trigger if job doesn't check-in every N days/hours/whatever)
- Get notified when Lambda function emits an error - e.g. http://docs.aws.amazon.com/lambda/latest/dg/with-scheduledevents-example.html
- Add JSON for IAM and/or CloudFormation and/or Terraform code for deploying
