import boto3
import logging
import os

# Clients
s3 = boto3.client('s3')
translate = boto3.client('translate')
sns = boto3.client('sns')

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info('Raw Event: {}'.format(event))
    print(event)
    
    # Extract Bucket- and Object names from Event Information
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_name = event['Records'][0]['s3']['object']['key']

    # Get the object from S3
    fileobj = s3.get_object(
        Bucket=bucket_name,
        Key=object_name
    ) 
    
    # Open the file object and read it into the variable filedata. 
    filedata = fileobj['Body'].read()
    
    # file data will be a binary stream.  We have to decode it and store it as string
    content = str(filedata.decode('utf-8'))

    # Send content from the input file to AWS translate
    response_translate = translate.translate_text(
        Text=content,
        SourceLanguageCode='auto',
        TargetLanguageCode='de'
    )
    
    # Send the translated text as SMS to a recipient
    response_sns = sns.publish(
        TopicArn=os.environ['sns_topic'],
        Message=response_translate['TranslatedText']
    )
    
    return {
        'statusCode': 200,
        'body': response_sns
    }