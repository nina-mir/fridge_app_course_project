# Credentials Folder

## The purpose of this folder is to store all credentials needed to log into your server and databases. This is important for many reasons. But the two most important reasons is
    1. Grading , servers and databases will be logged into to check code and functionality of application. Not changes will be unless directed and coordinated with the team.
    2. Help. If a class TA or class CTO needs to help a team with an issue, this folder will help facilitate this giving the TA or CTO all needed info AND instructions for logging into your team's server. 


# Blow is a list of items required. Missing items will causes points to be deducted from multiple milestone submissions.

1. Server URL or IP: http://ec2-34-224-23-175.compute-1.amazonaws.com
2. SSH username : ubuntu
3. SSH password or key: File TeamCSC103.pem
    <br> If a ssh key is used please upload the key to the credentials folder.
4. Database URL or IP and port used. Mysql HostName: refrigerator-db.c4p7z07xl4sc.us-east-1.rds.amazonaws.com Port: 3306.
    <br><strong> NOTE THIS DOES NOT MEAN YOUR DATABASE NEEDS A PUBLIC FACING PORT.</strong> But knowing the IP and port number will help with SSH tunneling into the database. The default port is more than sufficient for this class.
5. Database username: admin
6. Database password: password
7. Database name (basically the name that contains all your tables): refrigerator_db.
8. Instructions on how to use the above information.
To look at our web: just copy URL above and paste it on any browser. Use the command "ssh -i "TeamCSC103.pem" ubuntu@ec2-34-224-23-175.compute-1.amazonaws.com" to access our instance. If this command if needed "chmod 400 TeamCSC103.pem". 
To access our database, Use the command "mysql -h refrigerator-db.c4p7z07xl4sc.us-east-1.rds.amazonaws.com -P 3306 -u admin -p" using the terminal. After entering you will be prompted to enter password.
# Most important things to Remember
## These values need to kept update to date throughout the semester. <br>
## <strong>Failure to do so will result it points be deducted from milestone submissions.</strong><br>
## You may store the most of the above in this README.md file. DO NOT Store the SSH key or any keys in this README.md file.
