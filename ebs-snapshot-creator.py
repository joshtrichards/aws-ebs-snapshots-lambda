import boto3
import collections
import datetime
import os

ec = boto3.client('ec2')

def lambda_handler(event, context):
  
  # Get Current Region
  aws_region = os.getenv('AWS_REGION')  
  
  # Determine Which Instances To SnapShot
  instances = ec.describe_instances(
    Filters=[
      { 'Name': 'tag:Backup', 'Values': ['Yes'] },
    ]
  ).get(
    'Reservations', []
  )
  
  print "Found %d instances that need backing up" % len(instances)

  # Iterate Over Each Instance & SnapShot Volumes Not Explicitly Excluded From Backups
  for instance in instances:

    # Get Instance Object
    instance = instance['Instances'][0]

    # Determine Retention Period Based Upon Tags
    retention_days = 7
    destination_region = None
    instance_name = ""
    for tag in instance['Tags']:
      if tag['Key'] == 'RetentionDays' and tag['Value'] > 0:
        retention_days = int(tag['Value'])

      if tag['Key'] == 'DestinationRegion' and len(tag['Value']) > 0:
        destination_region = tag['Value']

      if tag['Key'] == 'Name' and len(tag['Value']) > 0:
        instance_name = tag['Value']

    print "Setting SnapShot retention period To %s days" % (retention_days)

    # Determine When We're Going To Delete This SnapShot
    delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
    delete_fmt = delete_date.strftime('%Y-%m-%d')

    # Set Default SnapShot Tags
    snapshot_tags = [
      { 'Key': 'DeleteOn', 'Value': delete_fmt },
      { 'Key': 'Type', 'Value': 'Automated' },
    ]

    # If We Want To Offsite This SnapShot, Set The Appropriate Tag
    if destination_region != None:
      snapshot_tags = snapshot_tags + [{ 'Key': 'DestinationRegion', 'Value': destination_region }]

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
      )['Volumes'][0]         

      # Set Default SnapShot Description
      description = '%s - %s (%s)' % ( 
        instance_name, 
        vol_id, 
        dev_name 
      )     
      
      if 'Tags' in volume:
        for tag in volume['Tags']:
          
          # Determine If Volume Has 'Backup' Flag Set To 'No' & Exclude From SnapShot If It Does
          if tag['Key'] == 'Backup' and tag['Value'] == 'No':
            snapshot_required = False            
          
          # Override Default Description With Volume Name If One Specified
          if tag['Key'] == 'Name':
            description = tag['Value']

            
      # We Don't Want To SnapShot Any Volume Explictly Excluded
      if snapshot_required == False:
        print "\tIgnoring EBS volume %s (%s) on instance %s - 'Backup' Tag set to 'No'" % (
          vol_id, 
          dev_name, 
          instance['InstanceId']
        )

        continue
      
      
      print "\tFound EBS volume %s (%s) on instance %s - Proceeding with SnapShot" % (
        vol_id, 
        dev_name, 
        instance['InstanceId']
      )         
        
      # Take SnapShot Of Volume
      snap = ec.create_snapshot(
        VolumeId=vol_id, 
        Description=description
      )
      
      if not (snap):
        print "\t\tSnapShot operation failed!"
        continue

      print "\t\tSnapshot %s created in %s of [%s]" % ( 
        snap['SnapshotId'], 
        aws_region, 
        description 
      )       
      
      print "\t\tRetaining snapshot %s of volume %s from instance %s (%s) for %d days" % (
        snap['SnapshotId'],
        vol_id,
        instance['InstanceId'],
        instance_name,
        retention_days,
      )

      # Tag The SnapShot To Facilitate Later Automated Deletion & Offsiting
      ec.create_tags(
        Resources=[snap['SnapshotId']],
        Tags=snapshot_tags
      )