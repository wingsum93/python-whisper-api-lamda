import boto3
from openai import OpenAI
import os

# Initialize the S3 client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Get the bucket name and file key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']

    # Download the file from S3
    download_path = '/tmp/' + file_key
    s3_client.download_file(bucket_name, file_key, download_path)

    # Call OpenAI Whisper API to transcribe the audio
    transcription = transcribe_audio_with_whisper(download_path)

    # Write the transcription to a text file and upload it to S3
    output_file_key = file_key + '.txt'
    s3_client.put_object(Body=transcription, Bucket=bucket_name, Key=output_file_key)

def transcribe_audio_with_whisper(file_path):
    # Here you'll need to implement the logic to call the OpenAI Whisper API
    # and transcribe the audio file. Return the transcription as a string.
    client = OpenAI()
    audio_file= open(file_path, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
        response_format="text"
    )
