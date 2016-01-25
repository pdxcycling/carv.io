import boto
import sys
import os
from boto.s3.key import Key
import re
from boto.ec2.connection import EC2Connection
from boto.manage.cmdshell import sshclient_from_instance

LOCAL_PATH = '/'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
bucket_name = os.getenv('S3_BUCKET')

conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
bucket = conn.get_bucket(bucket_name)


def get_file_list(bucket_list, file_extension):
    """
    Get list of files from S3 bucket

    Args:
        bucket_list: list of files in bucket
        file_extension: regex file extension filter

    Returns:
        a list of files in bucket
    """
    files = []
    for l in bucket_list:
        keyString = str(l.key)
        if re.search("\." + file_extension, keyString):
            files.append(keyString)
    return files


class EC2Master(object):
    """
    EC2 master. This class handles connecting to EC2 and finding available
    machines in the cluster.
    """
    def __init__(self):
        '''
        Default constructor for EC2Master.
        Automatically connects to EC2 upon instantiation
        '''
        AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.conn = EC2Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        self.ec2_conn = boto.ec2.connect_to_region('us-west-2')
        self.instances = []

    def get_ec2_instance_list(self):
        """
        Returns a list of running EC2 instances that
        can be used as workers.
        """
        reservations = self.ec2_conn.get_all_instances()
        for reservation in reservations:
            # Only those instances that are actively running
            if reservation.instances[0].state == 'running':
                print "-I- Running instance:", reservation.instances[0].id
                self.instances.append(reservation.instances[0])
            else:
                print "-I- Instance ignored:", \
                    reservation.instances[0].id, \
                    reservation.instances[0].state
        return self.instances

    def get_instance(self, instance_name):
        """
        Get a specific EC2 instance's object

        Args:
            instance_name - the name of the EC2 to find
        Returns:
            an object of a running EC2 instance
        """
        return self.ec2_conn.get_all_instances([instance_name])[0].instances[0]

    def get_ssh_client(self, instance):
        """
        Get an ssh instance for a specific EC2 instance

        Args:
            instance: an EC2 instance object
        Returns:
            ssh client object
        """
        return sshclient_from_instance(instance,
            ssh_key_file='/Users/fiannacci/.ssh/ec2_key.pem',
            user_name='ubuntu')

if __name__ == "__main__":
    ec2_conn = EC2Master()

    # go through the list of files
    bucket_list = bucket.list("raw_mp4/", "/")

    # Get list of movie files in bucket
    video_file_list = get_file_list(bucket_list, file_extension="mp4")
    num_files = len(video_file_list)

    # Get list of all EC2 instances
    instance_list = ec2_conn.get_ec2_instance_list()
    num_instances = len(instance_list)

    # Distribute files across all machines in the cluster for processing
    files_per_instance = int(num_files / num_instances) + 1
    print "Files per instance:", files_per_instance

    for i, instance_name in enumerate(instance_list):
        print instance_name
        ssh_client = ec2_conn.get_ssh_client(instance_name)

        # Set environmental variables
        ssh_client.run('export AWS_ACCESS_KEY_ID=\'' +
                       AWS_ACCESS_KEY_ID + '\'')
        ssh_client.run('export AWS_SECRET_ACCESS_KEY=\'' +
                       AWS_SECRET_ACCESS_KEY + '\'')

        # Create video directory
        ssh_client.run('mkdir /home/ubuntu/videos_to_process')

        # Move files to each instance for processing
        begin_index = i * files_per_instance
        end_index = (i+1) * files_per_instance - 1

        print begin_index, end_index
        for file_name in video_file_list[begin_index:end_index]:
            print bucket_name + '/' + file_name
            ssh_client.run('s3cmd get s3://' +
                           bucket_name + '/' + file_name +
                           ' /home/ubuntu/videos_to_process/')
