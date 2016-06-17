import boto3
import collections
import datetime

# Source Region - the region our instances are running in that we're backing up
source_region = 'us-west-2' 
copy_region = 'us-east-1'

#ec = boto3.client('ec2', region_name=source_region)

ec = boto3.client('ec2')

def lambda_handler(event, context):
    reservations = ec.describe_instances(
        Filters=[
            { 'Name': 'tag:Backup', 'Values': ['Yes'] },
        ]
    ).get(
        'Reservations', []
    )

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    print "Found %d instances that need backing up" % len(instances)

    to_tag = collections.defaultdict(list)

    for instance in instances:
        try:
            retention_days = [
                int(t.get('Value')) for t in instance['Tags']
                if t['Key'] == 'Retention'][0]
        except IndexError:
            retention_days = 7

        for dev in instance['BlockDeviceMappings']:
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']
            dev_name = dev['DeviceName']
            print "\tFound EBS volume %s (%s) on instance %s" % (
                vol_id, dev_name, instance['InstanceId'])

            # figure out instance name if there is one
            instance_name = ""
            for tag in instance['Tags']:
                if tag['Key'] != 'Name':
                    continue
                else:
                    instance_name = tag['Value']
            
            description = '%s - %s (%s)' % ( instance_name, vol_id, dev_name )

            # trigger snapshot
            snap = ec.create_snapshot(
                VolumeId=vol_id, 
                Description=description
                )
            
            if (snap):
                print "\t\tSnapshot %s created in %s of [%s]" % ( snap['SnapshotId'], source_region, description )
            to_tag[retention_days].append(snap['SnapshotId'])
            print "\t\tRetaining snapshot %s of volume %s from instance %s (%s) for %d days" % (
                snap['SnapshotId'],
                vol_id,
                instance['InstanceId'],
                instance_name,
                retention_days,
            )

            ## trigger copy of above snapshot out-of-region if an additional snapshot destination is defined ##
            if (copy_region):
                # open a client connection to the destination 
                addl_ec = boto3.client('ec2', region_name=copy_region)
                addl_snap = addl_ec.copy_snapshot(
                    SourceRegion=source_region,
                    SourceSnapshotId=snap['SnapshotId'],
                    Description=description,
                    DestinationRegion=copy_region
                )

                if (addl_snap):
                    print "\t\tSnapshot copy %s created in %s of [%s] from %s" % ( addl_snap['SnapshotId'], copy_region, description, source_region )
                #to_tag[retention_days].append(addl_snap['SnapshotId'])
                print "\t\tRetaining snapshot copy %s created in %s of volume %s from instance %s (%s) in %s for %d days" % (
                    addl_snap['SnapshotId'],
                    copy_region,
                    vol_id,
                    instance['InstanceId'],
                    instance_name,
                    source_region,
                    retention_days,
                )

    for retention_days in to_tag.keys():
        delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
        delete_fmt = delete_date.strftime('%Y-%m-%d')
        print "Will delete %d snapshots on %s" % (len(to_tag[retention_days]), delete_fmt)
        ec.create_tags(
            Resources=to_tag[retention_days],
            Tags=[
                { 'Key': 'DeleteOn', 'Value': delete_fmt },
                { 'Key': 'Type', 'Value': 'Automated' },
            ]
        )
