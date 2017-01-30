import boto3
import re
import datetime

ec = boto3.client('ec2')

"""
This function looks at *all* snapshots that have a "DeleteOn" tag containing
the current day formatted as YYYY-MM-DD. This function should be run at least
daily.
"""

def lambda_handler(event, context):
    account_ids = (boto3.client('sts').get_caller_identity()['Account'])
    
    delete_on = datetime.date.today().strftime('%Y-%m-%d')
        # limit snapshots to process to ones marked for deletion on this day
        # AND limit snapshots to process to ones that are automated only
        # AND exclude automated snapshots marked for permanent retention
    filters = [
        { 'Name': 'tag:DeleteOn', 'Values': [delete_on] },
        { 'Name': 'tag:Type', 'Values': ['Automated'] },
    ]
    snapshot_response = ec.describe_snapshots(OwnerIds=[account_ids], Filters=filters)

    for snap in snapshot_response['Snapshots']:
        for tag in snap['Tags']:
            if tag['Key'] != 'KeepForever':
                skipping_this_one = False
                continue
            else:
                skipping_this_one = True

        if skipping_this_one == True:
            print "Skipping snapshot %s (marked KeepForever)" % snap['SnapshotId']
            # do nothing else
        else:
            print "Deleting snapshot %s" % snap['SnapshotId']
            ec.delete_snapshot(SnapshotId=snap['SnapshotId'])