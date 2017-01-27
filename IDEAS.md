## ebs-snapshot-creator.py

### P1

- WIP: Out-of-region snapshot support - It should be possible to configure and create out-of-region snapshots without external tools
  - DONE: Copying a snapshot to an additional region should be possible within the creator (hardcoded in creator)
  - DONE: Enabling snapshot copying out-of-region should be easily configurable in the creator script (albeit still requiring a variable parameter change)
  - DONE: Only copy snapshot out of region if a copy_region is defined in the creator script
  - DONE: The out-of-region/copy snapshot functionality should be in its own dedicated job 
    - because snapshots can't be copied until they're in a completed state (and this enables getting closer to that)
    - Job/function is easy to understand (logical point of separation)
  - DONE: Copies of snapshots in the additional region should be tagged in the same manner as in-region snapshots (Automated: Yes, expiration info, etc.)
  - DONE: Enabling the copying (duplication) of a snapshot out-of-region should be configurable on a per instance basis
  - DONE: Out-of-region snapshots should be managed (for expiration/retention) just like in-region snapshots

### P2
- It should be possible to get automatically notified when the job (a Lambda function) emits an error
  - e.g. http://docs.aws.amazon.com/lambda/latest/dg/with-scheduledevents-example.html
- DONE: The required minimum IAM role policy should be provided

### P3
- It should be possible to configure multiple regions to copy (duplicate) snapshots into
- It should be possible to trigger a web hook (optionally / if configured) every time the creator job runs 
  - e.g. to use with PagerDuty to monitor if a job doesn't check-in every N days/hours/whatever
- ADDED CFN: Add JSON for IAM and/or CloudFormation and/or Terraform code and/or CLI/SH for deploying
- It should be possible to trigger snapshots of instance volumes in other regions besides the one that the creator is running in (or should it?)

## ebs-snapshot-manager.py

### P1
- Manage out-of-region snapshots too

### P2
- Get notified when Lambda function emits an error - e.g. http://docs.aws.amazon.com/lambda/latest/dg/with-scheduledevents-example.html
- Add support for retention of most recent X weeks to manager 
  - versus current only most recent X days support
  - to permit one-day-a-week going back X weeks snapshot retention/archiving support
- Add support for retention of most recent X months to manager
  - versus current only most recent X days support
  - to permit one-day-a-month going back X months snapshot retention/archiving support

### P3
- Trigger a optional (if configured) web hook every time it runs (e.g. to use with PagerDuty to trigger if job doesn't check-in every N days/hours/whatever)
- ADDED CFN: Add JSON for IAM and/or CloudFormation and/or Terraform code and/or CLI/SH for deploying

## ebs-snapshot-watcher.py

### P1
- Find the volume(s) without snapshot(s) and, unless tagged for being ignored, notify about them
- There should be detection of snapshot failures and easier alerting
  - Investigate failure scenarios for snapshot creator
  - Investigate how to improve notification/alerting on failure for snapshot creator
  - Thoughts:
    - due to design maybe either adding watchdog code to the manager when it sees configured instances not getting backed up to alert
    - or in the interest of modularity, creating a watchdog/alert/monitor function/job that looks for indications of problems (starting
      with configured instances not being recently backed up, obvious indictations of snapshot jobs failing in logs, expired snapshots 
      not being cleared, etc.)

### P2
- Get notified when Lambda function emits an error - e.g. http://docs.aws.amazon.com/lambda/latest/dg/with-scheduledevents-example.html
- Watch out-of-region snapshots too

### P3
- Trigger a optional (if configured) web hook every time it runs (e.g. to use with PagerDuty to trigger if job doesn't check-in every N days/hours/whatever)
- Add JSON for IAM and/or CloudFormation and/or Terraform code for deploying
