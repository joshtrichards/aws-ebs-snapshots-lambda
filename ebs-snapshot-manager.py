import boto3
import re
import datetime


aws_account = 'XXXX'

ec = boto3.client('ec2')

"""
This function looks at *all* snapshots that have a "DeleteOn" tag containing
the current day formatted as YYYY-MM-DD. This function should be run at least
daily.
"""

def lambda_handler(event, context):

        # Limit snapshots to process to ones that are automated only
        # AND exclude automated snapshots marked for permanent retention

    snapshot_response = ec.describe_snapshots(
        OwnerIds = [aws_account], 
        Filters = [
            { 'Name': 'tag:Type', 'Values': ['Automated'] },
        ]
    )

    today = datetime.datetime.today()

    # Remove snapshots tagged as "KeepForever"
    automated_snapshots = []

    for snap in snapshot_response['Snapshots']:

        skipping_this_one = False

        for tag in snap['Tags']:
            if tag['Key'] == 'KeepForever':
              print "Keeping forever snapshot: %s" %snap['SnapshotId']
              skipping_this_one = True

        if skipping_this_one == False:
            automated_snapshots.append(snap)

    # Process automated snapshots not tagged as "KeepForever"
    for snap in automated_snapshots:

        for tag in snap['Tags']:
            if tag['Key'] == 'DeleteOn':

              delete_on = datetime.datetime.strptime(tag['Value'],'%Y-%m-%d')

              if delete_on <= today:
                  print "Deleting snapshot %s" % snap['SnapshotId']
                  ec.delete_snapshot(SnapshotId=snap['SnapshotId'])


if __name__ == '__main__':
    lambda_handler(None, None)
