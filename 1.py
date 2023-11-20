import boto3
from openai import OpenAI
import os
import logging
import json


# Initialize the S3 client
s3_client = boto3.client('s3')
# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_secret():
    secret_name = "mySecretName"
    region_name = "myRegion"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        # Handle the exception here
        raise e
    else:
        # Decrypts secret using the associated KMS CMK
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret
        
def lambda_handler(event, context):
    logger.info("Event: " + json.dumps(event))

    # Get the bucket name and file key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']

    if 'mp3' not in file_key:
        logger.info("not tragger audio file type "+ json.dumps(event))
       
    # Download the file from S3
    download_path = '/tmp/' + file_key
    s3_client.download_file(bucket_name, file_key, download_path)

    # Call OpenAI Whisper API to transcribe the audio
    transcription = transcribe_audio_with_whisper(download_path)

    # Write the transcription to a text file and upload it to S3
    output_file_key = file_key + '.txt'
    s3_client.put_object(Body=transcription, Bucket=bucket_name, Key=output_file_key)

def transcribe_audio_with_whisper(file_path):
    # Retrieve the secret
    api_key = get_secret()
    
    client = OpenAI()
    client.api_key = api_key
    audio_file= open(file_path, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
        response_format="text"
    )
