import boto3
import json

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name = 'ap-south-1')
dynamodbTableName = 'employee'
dynamodb = boto3.resource('dynamodb',region_name = 'ap-south-1')
employeeTable = dynamodb.Table(dynamodbTableName)
bucketName = 'visitors-images-collections'

def lambda_handler(event, context):
    print(event)
    objectKey = event['queryStringParameters']['objectKey']
    image_bytes = s3.get_object(Bucket=bucketName, Key=objectKey)['Body'].read()
    response = rekognition.search_face_by_image(
        CollectionId = 'employees',
        Image = {'Bytes':image_bytes}
    )

    for match in response['FaceMatches']:
        print(match['Face']['FaceId'], match['Face']['Confidence'])

        face = employeeTable.get_item(
            Key={
                'rekognitionId': match['Face']['FaceId']
            }
        )
        if 'item' in face:
            print('Person Found: ', face['item'])
            return buildResponse(200, {
                'Message': 'Success',
                'firstName': face['item']['firstName'],
                'lastName': face['item']['lastName']
            })
    print('Person could not be recognized')
    return buildResponse(403, {'Message': 'Person Not Found'})
    
def buildResponse(statusCode, body=None):
    response={
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body)
    return response