import boto3
import collections
import datetime
import time

region = 'us-east-1'    # region we're running in (should be changed to be auto-determined

ec = boto3.client('ec2')


def lambda_handler(event, context):
    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag:Backup', 'Values': ['Yes']},
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

            description = '%s - %s (%s)' % (instance_name, vol_id, dev_name)

            # trigger snapshot
            snap = ec.create_snapshot(
                VolumeId=vol_id,
                Description=description
                )

            if (snap):
                print "\t\tSnapshot %s created in %s of [%s]" % (snap['SnapshotId'], region, description)

                # Tag snapshot
                delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
                delete_fmt = delete_date.strftime('%Y-%m-%d')
                print "Will delete %d snapshots on %s" % (len(to_tag[retention_days]), delete_fmt)

                # Tag snapshot, if fail try again
                count = 0
                while (count < 3):
                    try:
                        ec.create_tags(
                            Resources=[snap['SnapshotId']],
                            Tags=[
                                {'Key': 'DeleteOn', 'Value': delete_fmt},
                                {'Key': 'Type', 'Value': 'Automated'},
                            ]
                        )
                        count = 3
                    except Exception:
                        time.sleep(5)
                        count += 1

            print "\t\tRetaining snapshot %s of volume %s from instance %s (%s) for %d days" % (
                snap['SnapshotId'],
                vol_id,
                instance['InstanceId'],
                instance_name,
                retention_days,
            )


if __name__ == '__main__':
    lambda_handler(None, None)
