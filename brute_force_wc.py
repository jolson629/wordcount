import boto3
import json
import os
import sys
from configparser import RawConfigParser


# Brute force word count used to test ECS.

def getCmdLineParser():
    import argparse
    desc = 'Execute brute force word count'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-b', '--bucket', default=None,
                        help='S3 bucket')

    parser.add_argument('-r', '--region', default=None,
                        help='S3 bucket region')

    parser.add_argument('-k', '--inputKey', default=None,
                        help='input object in bucket')

    parser.add_argument('-o', '--outputKey', default = None,
                        help='output object to write')

    return parser



def main(argv):

   tmp = '/tmp'
   p = getCmdLineParser()
   args = p.parse_args()
   print('Starting processing %s/%s (%s)' % (args.bucket,args.inputKey,args.region))
   # Get the input set 
   if os.path.exists('%s/%s' % (tmp, args.inputKey)):
     os.remove('%s/%s' % (tmp, args.inputKey))
   s3 = boto3.resource('s3', region_name=args.region)
   try:
      s3.Bucket(args.bucket).download_file(args.inputKey, tmp+'/'+args.inputKey)
   # todo: figure out the proper exceptions here...
   except Exception as e:
      print('Error accessing %s/%s (%s). Error: %s' % (args.bucket, args.inputKey, args.region, e))
      print('Exiting...')
      sys.exit(-1)
      
   text = open('%s/%s' % (tmp, args.inputKey), 'r') 

   # Create an empty dictionary 
   d = dict() 
     
   # Loop through each line of the file 
   for line in text: 

      # Remove the leading spaces and newline character 
      line = line.strip() 

      # Convert the characters in line to  
      # lowercase to avoid case mismatch 
      line = line.lower() 

      # Split the line into words 
      words = line.split(' ') 

      # Iterate over each word in line 
      for word in words: 
        # Check if the word is already in dictionary 
        if word in d: 
            # Increment count of word by 1 
            d[word] = d[word] + 1
        else: 
            # Add the word to dictionary with count 1 
            d[word] = 1
   try:         
      s3.Object(args.bucket, args.outputKey).put(Body=json.dumps(d))
      print('Finished processing %s/%s. Wrote %s/%s (%s)' % (args.bucket,args.inputKey, args.bucket, args.outputKey, args.region))
   # todo: figure out the proper exceptions here...
   except Exception as e:
      print('Error writing %s/%s (%s). Error: %s' % (args.bucket, args.outputKey, args.region, e))
      print('Exiting...')
      sys.exit(-1)      
      
if __name__ == "__main__":
    main(sys.argv[1:])
