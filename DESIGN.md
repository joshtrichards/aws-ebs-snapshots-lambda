# Jobs

## v1/current

### ebs-snapshot-creator.py v1

- Creates primary snapshots (located in the same region as an instance).
- Runs once daily (but can be ran more often if desired)
- A creator should be running in every region that has source instances
  that have EBS volumes and are (or may be) configured to get snapshots
- Features
  - Look for instances (in same region as Lambda is running in) that have
    backups (snapshots) enabled
  - Find all connected EBS volumes on relevant instances
  - Tell AWS to create a snapshot of all found EBS volumes
  - Look for backup retention configuration on each relevant instance
  - If backup retention configuration found, use it to determine and set
    the expiration date on the created snapshots
  - If no backup retention configuration found, use a default of 7 days and
    set the expiration date on the created snapshots
  - For all created snapshots, sets a tag indicating they were
    automatically created by this tool
- Differentiators
  - Designed to run 100% from AWS Lambdas
  - Automatically handles snapshot expiration, not just creation
  - Entirely configured on a per instance basis using AWS's built-in tags
    - No external configuration files
    - No hardcoded configuration
    - No external database / file storage dependencies
    - Easy to customize per instance configuration
    - Easy to manage per instance configuration in orchestration tools
- Uses the following tags:
  - TBD

### ebs-snapshot-manager.py v1

- Deletes snapshots (located in the same region as Lambda is running in)
  that have hit their expiration date
- Features
  - Looks for snapshots (located in the same region as Lambda is running
    in) that that have hit their expiration date and have a tag indicating
    they were created by this tool. 
  - Pulls all needed information from snapshots themselves (which are, in
    turn, automatically tagged/configured from instance configuration)

## v2

- Differentiators (beyond already noted in v1)
  - No inter-region dependencies
    - All snapshot creation for instances in a given region handled by a
      Lambda in the same region
    - Service problems in one region do not impact cretion jobs in other
      regions
    - Multi-region snapshot creation (and replication, using new copier
      job) enabled without centralizing job management in one region
    - All jobs operate autonomously within region
    - All jobs operate autonomously across regions

### ebs-snapshot-creator.py v2
 
- No code changes over v1 other than tag adjustments to accomodate cleaner
  tag naming/design.
- Usage instructions added on how to use in situations where instances are
  running in multiple regions (hint: run a creator job in each relevant
  region)

### ebs-snapshot-manager.py v2

- No code changes over v1 other than tag adjustments to accomodate cleaner
  tag naming/design.
- Usage instructions added on how to use in situations where instances are
  running in multiple regions (hint: run a manager job in each relevant
  region)
- Usage instructions added on how to use in situations where snapshots are
  enabled for replication into additional regions (hint: run a manager job
  in each relevant region)

### ebs-snapshot-copier.py v2

- Copies any snapshots (located in the same region as Lamdba is running in)
  that are enabled for copying into additional regions, into those 
  additional specified regions
- Runs once daily (but can be ran more often if desired)
- A copier should be running in every region that has primary snapshots / 
  source instances that are (or may be) configured for replication into
  additional regions
- Features:
  - Pulls all configuration from snapshots themselves (which are, in turn,
    automatically tagged/configured from instance configuration)
  - Only copies snapshots that are in a completed state to avoid creating
    unusable snapshots
  - Does not copy non-primary snapshots (i.e. those not located in the same
    region as an instance) to prevent copying snapshots that have already
    been copied (and would otherwise create infinitely copying loops)
  - Replicates primary snapshot configuration (e.g. expiration dates)
  - Retains sufficient information to trace snapshot copies back to 
    original (primary) snapshots and source instances (because AWS snapshot
    copying processes do not retain this information and, worse, set bogus
    VolumeIds on out-of-region copied snapshots)

## v2 - original brainstorming

### ebs-snapshot-creator.py

- Creates primary snapshots (located in the same region as an instance).
- Runs once daily (but can we ran more often if desired)
- Uses the following tags:
  - TBD

### ebs-snapshot-copier.py

Copies primary snapshots to an additional region.
Uses the following tags:
- Snapshots: { PrimarySnapshotID (set), Description (copied), DeleteOn (copied), Type (copied) }
- Instances: { SnapshotsEnabled, SnapshotsRetention, SnapshotsExtraRegion1 }

### ebs-snapshot-manager.py

----

# Tags - Tracking 

## Snapshots

XXX Description			instance_name - vol_id (dev_name)					Set by creator
Description			instance_name (instance_id) - vol_id (dev_name)	- source_region		Set by creator
DeleteOn			YYYY-mm-dd								Set by creator
Type				Automated								Set by creator
Source_SnapshotId		Source SnapshotId in source region (if applicable)			Set by copier

# Tags - Configuration

## Snapshots

KeepForever			Yes									Set by operator/user if snapshot is to be retained outside of retention schedule

## Instances

Backup				Yes									Whether to snapshot (backup) volumes attached to this instance
Retention			# of days (7 is the default if not specified)				The number of days to retain snapshots for volumes attached to this instance
Copy_Dest			Name of an AWS region  							An additional region to copy snapshots to for volumes attached to this instance
Name				(whatever)								Used in snapshot description

----

# Functionality

## Overview & Status

- Not requiring the running of a management server instance to host, run, or trigger jobs				IMPLEMENTED
- Simple configuration based 100% on tagging of instances and snapshots 						IMPLEMENTED, mostly
- Creating snapshots													IMPLEMENTED
- Crash-consistent snapshots												IMPLEMENTED
- Copying snapshots to another region 											IMPLEMENTED, partially
- Expiring snapshots after specified period passes									IMPLEMENTED
- Retaining select snapshots indefinitely										IMPLEMENTED
- Managing snapshots copied to another region in same way as original snapshots						IN PROGRESS
- Automatically running job that handles creating snapshots on a specified schedule					IMPLEMENTED
- Automatically running job that handles copying snapshots to another region on a specified schedule			IMPLEMENTED, but refinement necessary
- Automatically running job that handles expiring snapshots on a specified schedule					IMPLEMENTED, but refinmement may be necessary
- Simple provisioning of jobs, scheduling, and permissions								TODO
- Try to run after database dumps have completed									TODO - EXTRA CREDIT
- Try to run after quieting filesystem (not sure yet)									TODO - EXTRA CREDIT
- Application-consistent snapshots											TODO - EXTRA CREDIT
- Reporting (not sure yet)												TODO
- Errors (not sure yet)													TODO 

## Not requiring the running of a management server instance to host, run, or trigger jobs

It is implemented as a set of Python based functions intended to run in AWS Lambda (which also handles
the job scheduling). This makes it self-contained and easier to setup, without any external resources
needed.

## Simple configuration based 100% on tagging of instances and snapshots

Easily readable (by humans and machines) AWS object tags are used to track as well as configure all 
aspects of the jobs. This permits easy management and changes without adding anything outside of 
AWS nor relying on external configuration files or hardcoded configuration of any sort.

## Creating snapshots 

The creator job (implemented in ebs-snapshot-creator.py) creates the primary snapshots (the ones in 
the same region as the instance volumes they are associated with). Instances which should have their
volumed backed up are configured by adding a tag with the name "Backup" and the value "Yes" to the 
instance. All volumes attached to a backup enabled instance of the type EBS will have snapshots 
taken of them.

## Crash-consistent snapshots												IMPLEMENTED

EBS snapshots are point-in-time back ups of the data on an EBS volume. This means that the snapshots
are exact copies of the data frozen at a specific point in time (i.e. all data across the volume is
"snapshotted" at a single point in time for consistency across the filesystem).

HOWEVER, there is a gotcha: If the instance is running (and it generally is for folks relying on 
snapshots as part of their backup strategy), EBS snapshots are crash-consistent. That is, whatever
is in memory on the instance is lost. It's as if someone pulled out the power cord of the computer,
pulled the volume out and copied it (the snapshot), then turned the computer back on. Of course
in EC2 your instance will just keep running so triggering EBS snapshots against running instances
is only *as if* someone did this.   

For some situations this is good enough. For situations it isn't. 

Modern filesystems with journaling support attempt to recover and deal with issues such as what 
happens when a "power cord is pulled". The same goes for database systems with recovery mechanisms
for similar situations. This, however, does not mean that data isn't lost. It simply means that
the filesystems and databases can return to a functioning reliable and probably good working state.
The cost for getting to this state is that a bit of data (for a narrow time window) may be tossed out
if it's suspect or incomplete.

Concerns can often be worked around by doing things like running database dumps via cron (that are just 
static files on-disk representing the contents of the database that then are effectively guaranteed
to be in a quiet/frozen state when the EBS snapshot runs ...whereas the raw live database data 
files themselves are *not* likely to be.)

Crash-consistent backups, and in turn EBS snapshots of running instances, are better than just copying
files (well, doing both are even better perhaps). The reason is because EBS snapshots are still 
point-in-time based, insuring consistency across the filesystem, whereas simply copying files has
time delays between when each file is copied. 

Interesting links: 

- [1](http://www.n2ws.com/blog/ebs-snapshots-crash-consistent-vs-application-consistent.html)
- [2](https://www.veeam.com/blog/how-to-create-a-consistent-vm-backup.html)
- [3](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSSnapshots.html)

## Copying snapshots to another region

The copier job (implemented in ebs-snapshot-copier.py) copies completed primary snapshots (the ones 
in the same region as the instance volumes they are associated with) to additional regions (only one 
additional is currently supported). Instances where it is desired that snapshots be copied to another
region are configured by adding a tag with the named "Auto_Snapshot_Copy1" and the value "us-east-1"
or similar region name. All volumes attached to a backup enabled instance with this parameter set to 
a valid region name will have their snapshots copied to this additional region.

Snapshots in the primary region are checked for counterparts in other regions (by looking for snapshots
in the other regions with the tag named "Source_SnapshotId" with a value equal to the primary snapshot's
SnapshotId[1].

Since we cannot copy primary snapshots that are in progress we attempt to workaround that issue in four 
ways:

- the copier job is independent of the creator job
- we schedule the creator job to run a fair bit after the creator job
- we only copy snapshots in a completed state 
- we pick up snapshots that were still not complete in the next job run

[1] We don't just compare snapshot Ids or even Volume IDs from the snapshots because AWS's copy snapshot 
function doesn't carry these over; the copied snapshot IDs are different than their originals and the 
volume Ids are bogus (I believe this is because internally they are actually copied to intermediate 
volumes for copying purposes only).

## Expiring snapshots after specified period passes

The retention period for snapshots of a given instance are specified by adding a tag to the instance with
the name "Retention" and the value of "#" of days to retain snapshots for. The default is 7 days if 
not specified.

The creator job looks for this Retention tag and based on it's setting (or using the default of 7 days if
it's not specified) sets a tag named "DeleteOn" on each snapshot at creation time, which specifies when 
that snapshot is to be kept until.

The manager job looks for snapshots tagged for deletion (per the "DeleteOn" tag) on the date it is 
running. It also, for safety, ignores snapshots not tagged as being automated (tag Type=Automated) as
well as those tagged with the tag "KeepForever".

The copier job doesn't do anything special for expiration, other than replicating the same tags (e.g. 
DeleteOn) and their values on all snapshot copies as they were set on the original snapshots.

## Retaining select snapshots indefinitely

A user/operator (or third-party script) can add a tag with the name "KeepForever" to any automated
snapshot and it will be retained indefinitely regardless of the expiration/retention configuration
for the instance that that snapshot is associated with. 

The manager job looks for snapshots tagged as "KeepForever" and ignores them for processing entirely.

The copier job replicates the KeepForever tag (if set) on primary snapshots to their counterparts
in other regions (although this not not done in real-time so it is best for the user/operator to 
set it manually on the copies too if they want to be certain).

## Managing snapshots copied to another region in same way as original snapshots					IN PROGRESS

The copier job makes sure that snapshots that are copied indicate which primary snapshots they are 
duplicates of by way of adding the tag named Source_SnapshotId with the relevant primary SnapshotId (we
have to do this because snapshot copies to other regions do not have relevant associated volume Ids nor 
any other reference to the source snapshots. So we create our own reference.) 

The copier job also duplicates the other key tags (DeleteOn and KeepForever).

The manager job checks for instances that have additional regions configured for copying, then 
processes snapshots in those regions in the same way as the primary instance region.

## Automatically running job that handles creating snapshots on a specified schedule					IMPLEMENTED, but refinement necessary

Currently we rely on AWS Lambda's built-in CloudEvent event of "rate(1 day)" to run daily.

To ensure the creator job runs before the copier we may need to be more specific with a time-of-day.

## Automatically running job that handles copying snapshots to another region on a specified schedule			IMPLEMENTED, but refinement necessary

Currently we rely on AWS Lambda's built-in CloudEvent event of "rate(1 day)" to run daily.

To ensure the copier job runs well after the creator job we may need to be more specific with a time-of-day.

## Automatically running job that handles expiring snapshots on a specified schedule					IMPLEMENTED, but refinmement may be necessary

Currently we rely on AWS Lambda's built-in CloudEvent event of "rate(1 day)" to run daily.

It doesn't seem like it really matters wheher the manager runs before, after, or even during the creator or 
copier jobs. 

## Simple provisioning of jobs, scheduling, and permissions								TODO

Phase 1: Permissions should be in JSON
Phase 2: S3 source for loading jobs
Phase 3: CloudFormation for IAM provisioning + provisioning jobs + loading function code from S3 + event scheduling

## Try to run after database dumps have completed									TODO - EXTRA CREDIT

Phase I: Job scheduling coordination + we'll at worst have the prior day's dump
Phase II: webhook? some other trigger for the job?

## Try to run after quieting filesystem (not sure yet)									TODO - EXTRA CREDIT

Phase I: Ignore
Phase II: fsfreeze + webhook/some other trigger for the job?

## Application-consistent snapshots											TODO - EXTRA CREDIT

If the fsfreeze mentioned in the prior section is implemented, then in theory this is do-able.
For Windows boxes, VSS equivalent may be an option.
Since EBS snapshots are point-in-time, once the snapshot starts, the freeze operation can be released ...even prior to the completion of the snapshot.
[1](http://www.n2ws.com/blog/ebs-snapshots-crash-consistent-vs-application-consistent.html)

## Reporting (not sure yet)												TODO
## Errors (not sure yet)												TODO 
