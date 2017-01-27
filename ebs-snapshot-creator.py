import boto3
import collections
import datetime
import os

ec = boto3.client('ec2')

def lambda_handler(event, context):
	
	# Get Current Region
    aws_region = os.getenv('AWS_REGION')
    
    # Get Retention Period From Environment Variable Or Assume Default If Not Specified
    retention_days = int(
        os.getenv(
            'RETENTION_DAYS', 
            7
        )
    )
    
    print "Setting SnapShot retention period To %s days" % (retention_days)
	
	# Determine Which Instances To SnapShot
    instances = ec.describe_instances(
        Filters=[
            { 'Name': 'tag:Backup', 'Values': ['Yes'] },
        ]
    ).get(
        'Reservations', []
    )
    
    print "Found %d instances that need backing up" % len(instances[0]['Instances'])

    # Initialise Dictionary Objects To Store Tags In
    to_tag = collections.defaultdict(list)

    # Iterate Over Each Instance & SnapShot Volumes Not Explicitly Excluded From Backups
    for instance in instances[0]['Instances']:

        # List All Volumes Attached To The Instance
        for dev in instance['BlockDeviceMappings']:
            
            # Set Variable Defaults
            snapshot_required = True
            volume_name = None
            
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']
            dev_name = dev['DeviceName']
            
            # Get a Volume Object Based Upon Volume ID
            volume = ec.describe_volumes(
                VolumeIds=[vol_id,]
            )
            
            vol = volume['Volumes'][0]
            if 'Tags' in vol:
                for tag in vol['Tags']:
                    
                    # Determine If Volume Has 'Backup' Flag Set To 'No' & Exclude From SnapShot If It Does
                    if tag['Key'] == 'Backup' and tag['Value'] == 'No':
                        snapshot_required = False
                       
                    # Determine If Volume Has a Name Specified     
                    if tag['Key'] == 'Name':
                        volume_name = tag['Value']
                        
            # Exit This Loop If SnapShot Not Required
            if snapshot_required == False:
                print "\tIgnoring EBS volume %s (%s) on instance %s - 'Backup' Tag set to 'No'" % (
                    vol_id, 
                    dev_name, 
                    instance['InstanceId']
                )
            
            else:
                print "\tFound EBS volume %s (%s) on instance %s - Proceeding with SnapShot" % (
                    vol_id, 
                    dev_name, 
                    instance['InstanceId']
                )
    
                # Determine EC2 Instance Name (If Present)
                instance_name = ""
                for tag in instance['Tags']:
                    if tag['Key'] != 'Name':
                        continue
                    else:
                        instance_name = tag['Value']
                        
                # Determine SnapShot Description (Use Volume Name If Specified)
                if volume_name == None:
                    description = '%s - %s (%s)' % ( 
                        instance_name, 
                        vol_id, 
                        dev_name 
                    )
                else:
                    description = volume_name
                    
                # Trigger SnapShot
                snap = ec.create_snapshot(
                    VolumeId=vol_id, 
                    Description=description
                    )
                
                if (snap):
                    print "\t\tSnapshot %s created in %s of [%s]" % ( 
                        snap['SnapshotId'], 
                        aws_region, 
                        description 
                    )
                
                # Tag The SnapShot To Facilitate Later Automated Deletion
                to_tag[retention_days].append(snap['SnapshotId'])
                
                print "\t\tRetaining snapshot %s of volume %s from instance %s (%s) for %d days" % (
                    snap['SnapshotId'],
                    vol_id,
                    instance['InstanceId'],
                    instance_name,
                    retention_days,
                )                

    for retention_days in to_tag.keys():
        delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
        delete_fmt = delete_date.strftime('%Y-%m-%d')
        print "Will delete %d snapshots from %s on %s" % (
            len(to_tag[retention_days]),
            aws_region,
            delete_fmt
        )
        
        ec.create_tags(
            Resources=to_tag[retention_days],
            Tags=[
                { 'Key': 'DeleteOn', 'Value': delete_fmt },
                { 'Key': 'Type', 'Value': 'Automated' },
            ]
        )   