import boto3, logging, config

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
bucket_name = config['S3_BUCKET_NAME']
bkt = s3.Bucket(bucket_name)


def compose(filelists, newfilename):
    try:
        contents = ''
        for filename in filelists:
            contents += bkt.Object(filename).get()['Body'].read()

        bkt.Object(newfilename).put(Body=contents)
        return True
    except:
        return False


def exists(key):
    logging.info('Loading from bucket {0}'.format(key))
    result = False
    try:
        bkt.Object(key).load()
        result = True
    except:
        pass

    return result


def list_objects(key, next=None, last_result=[]):
    if next:
        temp_result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=key, ContinuationToken=next)
    else:
        temp_result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=key)

    last_result = last_result + temp_result['Contents']
    if temp_result['IsTruncated']:
        return list_objects(key, next=temp_result['NextContinuationToken'], last_result=last_result)

    return last_result


def read(key, encoding=None):
    logging.info('Reading from bucket {0}'.format(key))
    result = bkt.Object(key).get()['Body'].read()
    if encoding:
        result = result  # .decode(encoding)

    return result


def write(key, contents, encoding=None):
    if encoding:
        contents = contents  # .encode(encoding)

    logging.info('Writing to bucket {0}'.format(key))
    try:
        bkt.Object(key).put(Body=contents)
        return True
    except:
        return False


def delete(key):
    bkt.Object(key).delete


def copy2(srcfilename, dstfilename):
    bkt.copy({'Bucket': bucket_name, 'Key': srcfilename}, dstfilename)


def getsize(key):
    return bkt.lookup(key).size
