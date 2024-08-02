import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name = 'ap-south-1')
dynamodbTableName = 'employee'
dynamodb = boto3.resource('dynamodb',region_name = 'ap-south-1')
employeeTable = dynamodb.Table(dynamodbTableName)

def lambda_handler(event, context):
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    try:
        response = index_employee_image(bucket, key)
        print(response)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            faceId = response['FaceRecords'][0]['Face']['FaceId']
            name = key.split('.')[0].split('_')
            firstname = name[0]
            lastname = name[1]
            register_employee(faceId, firstname, lastname)
        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket))
        raise e
    
def index_employee_image(bucket, key):
    response = rekognition.index_faces(
        Image={
            'S3Object':
            {
                'Bucket': bucket,
                'Name': key
            }
        },
        CollectionId = "employees"  #We will create this later
    )
    return response

def register_employee(faceId, firstname, lastname):
    employeeTable.put_item(
        Item={
            'rekognitionId': faceId,
            'firstName': firstname,
            'lastName': lastname
        }
    )