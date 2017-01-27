import boto3
import collections
import datetime
import os

ec = boto3.client('ec2')

def lambda_handler(event, context):

	# Get Current Region
	aws_region = os.getenv('AWS_REGION')

	# Get All SnapShots With 'Offsite' Tag Set
	snapshots = ec.describe_snapshots(
		Filters=[
			{ 'Name': 'tag-key', 'Values': ['DestinationRegion'] },
            { 'Name': 'status', 'Values': ['completed'] },
		]
	)

	for snapshot in snapshots['Snapshots']:

		# Reset Our Destination Region
		destination_region = None

		# Obtain Tags From Source SnapShot
		for tag in snapshot['Tags']:
			
			# Obtain Destination Region From Source Snapshot Tag
			if tag['Key'] == 'DestinationRegion':
				destination_region = tag['Value']

			# Check If We Need To Do A Copy Or Not
			if destination_region == aws_region:

				print "\tDestination Region %s is the same as current region (%s) - skipping copy" % (
					destination_region,
					aws_region
				)

				continue

		# Construct ec2 Client For Secondary Region
		secondary_ec = boto3.client('ec2', region_name=destination_region)

		# Determine If There's An Off-Site Copy Of This SnapShot
		os_snapshots = secondary_ec.describe_snapshots(
			Filters=[
				{ 'Name': 'tag:SourceSnapshotId', 'Values': [snapshot['SnapshotId']] },
				{ 'Name': 'status', 'Values': ['pending','completed'] },
			]
		)

		# We Only Want To Delete Where Snapshot Has Copied Successfully
		if len(os_snapshots['Snapshots']) >= 1:

			snapshot_states = [d['State'] for d in os_snapshots['Snapshots']]

			if 'pending' in snapshot_states:
				print "\tThere is at least 1 Snapshot copy pending in %s - skipping delete & copy" % (
					destination_region
				)
				
				continue					

			print "\t\tFound a corresponding Snapshot with Id %s in %s created from Snapshot %s" % (
				os_snapshots['Snapshots'][0]['SnapshotId'],
				destination_region,				
				snapshot['SnapshotId']
			)

			print "Deleting source Snapshot %s from %s" % (
				snapshot['SnapshotId'],
				aws_region
			)

			ec.delete_snapshot(
				SnapshotId=snapshot['SnapshotId']
			)

			continue

		# Create Copy Of Snapshot Because One Doesn't Exist
		os_snapshot = secondary_ec.copy_snapshot(
			SourceRegion=aws_region,
			SourceSnapshotId=snapshot['SnapshotId'],
			Description=snapshot['Description'],
			DestinationRegion=destination_region
		)

		# If Snapshot Copy Executed Successfully, Copy The Tags
		if (os_snapshot):

			print "\t\tSnapshot copy %s created in %s of %s from %s" % (
				os_snapshot['SnapshotId'],
				destination_region,
				snapshot['SnapshotId'],
				aws_region
			)

			# Add Tags To Off-Site SnapShot
			destination_snapshot_tags = snapshot['Tags'] + [{ 'Key': 'SourceSnapshotId', 'Value': snapshot['SnapshotId'] }]
			secondary_ec.create_tags(
				Resources=[os_snapshot['SnapshotId']],
				Tags=destination_snapshot_tags					
			)

			# Add Tags To Source SnapShot
			ec.create_tags(
				Resources=[snapshot['SnapshotId']],
				Tags=[
					{ 'Key': 'OffsiteSnapshotId', 'Value': os_snapshot['SnapshotId'] },
				]
			)