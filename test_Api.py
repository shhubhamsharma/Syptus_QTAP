import StringIO, pycurl, json
import json,certifi
import json
import pandas as pd
from glob import glob
# Change the following to your own username, password and API key

class QTSAPIHelper:

    # Constructor to set endpoint for reuse
    def __init__(self, endpoint):
        self.endpoint = endpoint
        
    # Returns the result of a login attept with the given parameters.
    def login(self, username, password, apiKey):
            url = self.endpoint + "login"
            json_array = {'username':username, 'password':password, 'apiKey':apiKey}
            result = self.callAPI(url, json_array)
            return result
        
    # Returns a list of surveys
    def listSurveys(self, pageSize, pageNumber):
            url = self.endpoint + "listSurveys"
            json_array = {'pageSize':pageSize, 'pageNumber':pageNumber}
            result = self.callAPI(url, json_array)
            return result       
        
    # Returns survey reponses for the given survey
    def getSurveyResponses(self, surveyId, pageSize, pageNumber, fromDate, toDate):
            url = self.endpoint + "getSurveyResponses"
            json_array = {'surveyId':surveyId, 'pageSize':pageSize, 'pageNumber':pageNumber}
            if fromDate and toDate:
                json_array['fromDate'] = fromDate
                json_array['toDate'] = toDate

            result = self.callAPI(url, json_array)
            return result       
                
    # Function to call API with given data
    def callAPI(self, url, json_array):
            data = json.dumps(json_array, encoding="utf-8")
            length = str(len(data))
            headers = ['Content-Type: application/json', 'Content-Length: '+length]
            cookies_file = "/tmp/cookies.txt"
            print "Cnnecting to: " + url
            print "Post Data: " + data
            result = StringIO.StringIO()
            c = pycurl.Curl()
            c.setopt(pycurl.CAINFO,certifi.where())
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.POSTFIELDS, data)
            c.setopt(pycurl.HTTPHEADER, headers)
            c.setopt(pycurl.COOKIEFILE, cookies_file)
            c.setopt(pycurl.COOKIEJAR, cookies_file)
            c.setopt(pycurl.WRITEFUNCTION, result.write)
        #c.setopt(pycurl.SSL_VERIFYPEER, 0)
        #c.setopt(pycurl.SSL_VERIFYHOST, 0)
            c.perform()
            c.close()
            return result

username = "Upworkapi"
password = "Dino54321"
apiKey = "PALKIJ1E2I80NVFVLNZOWMUN4I788IYN"

# Constants
CODE_LOGIN_SUCCESS = 10
CODE_LIST_SURVEYS_SUCCESS = 20
CODE_GET_SURVEY_RESPONSES_SUCCESS = 30
ENDPOINT_URL = "https://www.quicktapsurvey.com/api-v1/"

# instantiate api helper class
apiHelper = QTSAPIHelper(ENDPOINT_URL)

# call login method
loginJson = apiHelper.login(username, password, apiKey)

loginResult = json.loads(loginJson.getvalue())
print("###########")
resultCode = int(loginResult["resultCode"])
def convert(x):
	''' Convert a json string to a flat python dictionary
	which can be passed into Pandas. '''
	ob = json.loads(x)
	for k, v in ob.items():
		if isinstance(v, list):
			ob[k] = ','.join(v)
		elif isinstance(v, dict):
			for kk, vv in v.items():
				ob['%s_%s' % (k, kk)] = vv
			del ob[k]
	return ob


if resultCode == CODE_LOGIN_SUCCESS:
    print "Login Successful.";
    pageSize = 25
    pageNumber = 1
    listSurveysJson = apiHelper.listSurveys(pageSize, pageNumber)
    listSurveysResult = json.loads(listSurveysJson.getvalue())
    for json_filename in glob(listSurveysResult):
        csv_filename = '%s.csv' % json_filename[:-5]
        print 'Converting %s to %s' % (json_filename, csv_filename)
        df = pd.DataFrame([convert(line) for line in file(json_filename)])
        df.to_csv(csv_filename, encoding='utf-8', index=False)
    
    resultCode = int(listSurveysResult["resultCode"])
    
    if resultCode == CODE_LIST_SURVEYS_SUCCESS:
        print "List Surveys Successful.";
        surveyId = listSurveysResult["surveyList"][0]["surveyId"]
        pageSize = 25
        pageNumber = 1
    # sample date format: 2014-09-09 17:25:34 -0400
        fromDate = ""
        toDate = ""
        getSurveyResponsesJson = apiHelper.getSurveyResponses(surveyId, pageSize, pageNumber, fromDate, toDate)
        getSurveyResponsesResult = json.loads(getSurveyResponsesJson.getvalue())
        resultCode = int(getSurveyResponsesResult["resultCode"])
        if resultCode == CODE_GET_SURVEY_RESPONSES_SUCCESS:
            print "Get Survey Responses Successful.";
            print "Responses: " + str(getSurveyResponsesResult)
        else:
            print "Get Survey Responses Failed with Code: " + str(resultCode);
        
    else:
        print "List Surveys Failed with Code: " + str(resultCode);
    
else:
    print "Login Failed with Code: " + str(resultCode);
    
