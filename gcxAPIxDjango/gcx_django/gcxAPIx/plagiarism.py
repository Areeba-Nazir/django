import re
import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
import urllib.request
from django.core.serializers.json import DjangoJSONEncoder
from .factory import getConnection
from .auth import bearer_auth


# ---#------------------------------------------------------------------------------------------#
# --- PLAGIARISM CHECKER SECTION #
# ----------------------------------------------------------------------------------------------#


@api_view(['GET', 'POST'])
@bearer_auth
def checkPlagiarism_break_data_grm(request, *args, **kwargs):
    if 'access_token' in request.data and 'text' in request.data:
        access_token = request.data['access_token']
        text = request.data['text']
    else:
        error_response = {'response': 'Please Provide all parameters.', 'status': 'Failed'}
        return Response(error_response, status=status.HTTP_206_PARTIAL_CONTENT)
    token = "KW#2TI7G30fA(V"
    if token == access_token:
        # For Dummy Data
        # hash_token = "zJjoDRKUtoXnMxJpxVnKMw=="
        # req_token = "NzBkMjM3NTFiZGEzODYxOTgxOTAmMjI2OTNtYTNjSPECIALtoKEn"
        # For RealTime Data
        hash_token = "56XHi6B00k0Ct+CAa8Q6HQ=="
        req_token = "Mjk0N2Y5YzY4Mjk0YTY2NWE5ZWE1OTg1ODkzZTNm"
        req_hash = hash_token
        token = req_token
        # text = "Navy Divers operate anywhere from the shallow waters of coral reefs and harbors around the world to the freezing depths beneath icebergs, accomplishing specialized tasks below the surface,
        # with no margin for error. Your job as a Diver could encompass many specialties, including: Performing wreckage salvage operations and underwater repairs. Conducting harbor and waterway clearance
        # operations. Assisting in construction and demolition projects. Executing search and rescue missions. Performing deep submergence operations and saturation diving, which could involve living and
        # working at extreme depths for days or weeks at a time. Supporting military and civilian law enforcement agencies. Serving as technical experts for diving evolutions for numerous military Special
        # Operations units. Provide security, communications and other logistics during Expeditionary Warfare missions. Carry out ship and submarine maintenance, including inspection and repair"
        # For Dummy Data
        # url = "https://api.plagiarismsoftware.org/v5/break_data_grm"
        # For RealTime Data
        url = "https://api.plagiarismsoftware.org/v5/break_data"
        json_response = {"req_hash": req_hash, "token": token, "content": text}
        json_response = json.dumps(json_response)
        '''req_data = '{"req_hash":"zJjoDRKUtoXnMxJpxVnKMw==","token":"NzBkMjM3NTFiZGEzODYxOTgxOTAmMjI2OTNtYTNjSPECIALtoKEn","content":"Navy Divers operate anywhere from the shallow waters of coral reefs 
        and harbors around the world to the freezing depths beneath icebergs, accomplishing specialized tasks below the surface, with no margin for error. Your job as a Diver could encompass many specialties, 
        including: Performing wreckage salvage operations and underwater repairs. Conducting harbor and waterway clearance operations. Assisting in construction and demolition projects. Executing search and 
        rescue missions. Performing deep submergence operations and saturation diving, which could involve living and working at extreme depths for days or weeks at a time. Supporting military and civilian 
        law enforcement agencies. Serving as technical experts for diving evolutions for numerous military Special Operations units. Provide security, communications and other logistics during Expeditionary 
        Warfare missions. Carry out ship and submarine maintenance, including inspection and repair."}'''
        payload = {'raw_data': json_response}
        files = []
        headers = {}
        if text:
            # response = {'response': "Copy krta ha sasura"}
            data = requests.request("POST", url, headers=headers, data=payload, files=files)
            response = data.json()
        else:
            response = {"code": status.HTTP_206_PARTIAL_CONTENT, "reason": "Content is empty."}
            #response = json.dumps(response)
    else:
        print("Plag Break Data Accessed with wrong token.")
        json_response = {"response": 'Wrong Token'}
        return Response(json_response, status=status.HTTP_401_UNAUTHORIZED, )
    return Response(response, status=status.HTTP_200_OK, )


################################################################################################


@api_view(['GET', 'POST'])
@bearer_auth
def checkPlagiarism_grm_response(request, *args, **kwargs):
    if 'access_token' in request.data and 'content_id' in request.data and 'sentence_ids' in request.data:
        access_token = request.data['access_token']
        content_id = request.data['content_id']
        sentence_ids = request.data['sentence_ids']
        ex_url = request.data['exclude'] if 'exclude' in request.data else ""
    else:
        content = request.get_json(silent=True)
        access_token = content['access_token']
        content_id = content['content_id']
        sentence_ids = content['sentence_ids']
        ex_url = content['exclude'] if 'exclude' in content else ""
    token = "KW#2TI7G30fA(V"
    if token == access_token:
        # For Dummy Data
        # hash_token = "zJjoDRKUtoXnMxJpxVnKMw=="
        # req_token = "NzBkMjM3NTFiZGEzODYxOTgxOTAmMjI2OTNtYTNjSPECIALtoKEn"
        # For RealTime Data
        hash_token = "56XHi6B00k0Ct+CAa8Q6HQ=="
        req_token = "Mjk0N2Y5YzY4Mjk0YTY2NWE5ZWE1OTg1ODkzZTNm"
        # text_id = "52971"
        # sentence_ids = ["445863"]
        arr = sentence_ids.strip().split(',')
        # print(arr)
        req_hash = hash_token
        token = req_token
        content_id = content_id
        query = arr
    else:
        print("Check Plag accessed with wrong token.")
        json_response = 'Wrong Token'
        return Response(json_response, status=status.HTTP_401_UNAUTHORIZED, )
    # For Dummy Data
    # url = "https://api.plagiarismsoftware.org/v5/checkPlag_grm"
    # For RealTime Data
    url = "https://api.plagiarismsoftware.org/v5/check_plagv4"
    json_response = {"req_hash": req_hash, "token": token, "content_id": content_id, "query": query}
    json_response = json.dumps(json_response)
    # print(json_response)
    payload = {'raw_data': json_response}
    files = []
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    respp = response.json()
    index = 0
    if respp["data"][0]['is_plag'] == '1':
        for url in respp["data"][0]["details"]["webs"]:
            respp["data"][0]["details"]["webs"][index]['url'] = re.sub("[/]+$", "", url['url'])
            index += 1
        if ex_url != '':
            urls = respp["data"][0]["details"]["webs"]
            for item in urls:
                if re.sub("[/]+$", "", ex_url) == item['url']:
                    respp["data"][0]["details"]["webs"].remove(item)
            if len(respp["data"][0]["details"]["webs"]) < 1:
                respp["data"][0]["is_plag"] = '0'
                respp["data"][0]["details"]["unique"] = True
    return Response(respp, status=status.HTTP_200_OK, )


################################################################################################


@api_view(['GET', 'POST'])
@bearer_auth
def getPlagCompareText(request, *args, **kwargs):
    """ Doc """
    if 'textID' in request.data:
        textID = request.data['textID']
    else:
        content = request.get_json(silent=True)
        textID = content['textID']
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(
        """SELECT * FROM plag_compare_text WHERE id = '%s' """ % textID)
    rows = cur.fetchall()
    url = (rows[0][1])
    page = urllib.request.urlopen(url)
    source = page.read()
    source = source.decode("utf-8")
    data = {'updatePlagiarism': '1', 'contents': rows, 'pageSource': source}
    conn.close()
    #json_response = json.dumps(data, cls=DjangoJSONEncoder)
    return Response(data, status=status.HTTP_200_OK, )
