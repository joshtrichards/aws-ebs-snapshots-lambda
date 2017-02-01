import boto3
import collections
import datetime
import operator


aws_account = 'XXXX'
source = 'us-east-1'
destination = 'sa-east-1'

client = boto3.client('ec2', source)
foreign_client = boto3.client('ec2', destination)


def copy_latest_snapshot():

    response = client.describe_snapshots(
        Filters=[
            { 'Name': 'tag:Type', 'Values': ['Automated'] },
            { 'Name': 'status', 'Values': ['completed'] },

        ]
    )

    if len(response['Snapshots']) == 0:
        raise Exception("No automated snapshots found")


    snapshots_per_project = {}

    for snapshot in response['Snapshots']:

      if snapshot['Description'] not in snapshots_per_project.keys():
          snapshots_per_project[snapshot['Description']] = {}


      snapshots_per_project[snapshot['Description']][snapshot['SnapshotId']] = snapshot['StartTime']


    for project in snapshots_per_project:

      sorted_list = sorted(snapshots_per_project[project].items(), key=operator.itemgetter(1), reverse=True)

      copy_name = project + " - " + sorted_list[0][1].strftime("%Y-%m-%d")

      print("Checking if '" + copy_name + "' is copied")

      # Check if the snapshot was copied into destination
      response = foreign_client.describe_snapshots(
          Filters=[
              { 'Name': 'description', 'Values':[copy_name] },
          ]
      )

      if len(response['Snapshots']) == 0:
          print "'%s' not found" %copy_name

          foreingSnapshot = foreign_client.copy_snapshot(
              Description=  copy_name,
              SourceRegion=source,
              DestinationRegion=destination,
              SourceSnapshotId= sorted_list[0][0],
          )

          print("Copying '" + copy_name + "' to " + destination)


      if len(response['Snapshots']) == 1:
          print "'%s' already copied!" %copy_name

    return

def remove_old_snapshots():

    response = foreign_client.describe_snapshots(
        OwnerIds=[aws_account],
        Filters=[
            { 'Name': 'status', 'Values': ['completed'] },
        ]
    )

    if len(response['Snapshots']) == 0:
        raise Exception("No snapshots in "+ destination + " found")

    snapshots_per_project = {}

    #print "snapshots: %s" %response['Snapshots']


    for snapshot in response['Snapshots']:

        short_description = (snapshot['Description'])[0:snapshot['Description'].find(')')+1]

        if short_description not in snapshots_per_project.keys():
            snapshots_per_project[short_description] = {}


        snapshots_per_project[short_description][snapshot['SnapshotId']] = snapshot['StartTime']


    for project in snapshots_per_project:
        if len(snapshots_per_project[project]) > 1:
            sorted_list = sorted(snapshots_per_project[project].items(), key=operator.itemgetter(1), reverse=True)

            to_remove = [i[0] for i in sorted_list[1:]]

            for snapshot in to_remove:
                print("Removing " + snapshot)
                foreign_client.delete_snapshot(
                    SnapshotId=snapshot
                )


def lambda_handler(event, context):
    copy_latest_snapshot()
    remove_old_snapshots()

if __name__ == '__main__':
  lambda_handler(None, None)
