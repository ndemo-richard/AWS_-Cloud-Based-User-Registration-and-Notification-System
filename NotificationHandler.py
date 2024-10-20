import json
import boto3
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize DynamoDB and SNS clients
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

def lambda_handler(event, context):
    logging.info("Received event: %s", json.dumps(event))

    try:
        user_id = event['userName']
        email = event['request']['userAttributes']['email']

        logging.info(f"User confirmed: {user_id}, Email: {email}")

        # Access DynamoDB Table
        table = dynamodb.Table('UserPreferences')

        # Store user details in DynamoDB
        table.put_item(
            Item={
                'UserID': user_id,
                'Email': email,
                'NotificationPreference': 'Email'
            }
        )
        logging.info("User details saved to DynamoDB")

        # Subscribe the user's email to the SNS topic
        try:
            sns.subscribe(
                TopicArn='arn:aws:sns:us-east-1:867093160463:UserNotifications',  # Replace with your SNS Topic ARN
                Protocol='email',
                Endpoint=email
            )
            logging.info(f"User {email} subscribed to SNS topic")
        except Exception as sub_error:
            logging.error(f"Error subscribing user {email} to SNS topic: {str(sub_error)}")
            # You can choose to continue or return here if you don't want the process to continue.
            # return event

        # Send notification via SNS
        message = f"Hello {user_id}, your account has been successfully created!"
        response = sns.publish(
            TopicArn='arn:aws:sns:us-east-1:867093160463:UserNotifications',  # Replace with your SNS Topic ARN
            Message=message,
            Subject="Account Created"
        )
        logging.info("SNS publish response: %s", response)

        # Return the event as required by Cognito Post Confirmation trigger
        return event

    except Exception as e:
        logging.error("Error occurred: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps(f"An error occurred: {str(e)}")
        }

