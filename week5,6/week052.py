import os, sys
import urllib.request
import datetime, time
import json
import pandas as pd

#serviceKey = "s9CuSdYlF8MMsvHSesTMknvCXypbgH4qkKBQnYJef6KoOyY6SNBfCLafHV6WyOM2Ac1pARCLRHv3HFaMrehU4g%3D%3D"
serviceKey = "J3%2BczV4vMANbI6HHxJVrA5xklryjiDDR0TGMHyI02oja92z877l5HSMwRGWDZlFjWZ6nzm7Jk4C23JQEVbnD7Q%3D%3D"

# [CODE 1]
def getRequestUrl(url):  #url=출입국 관광 통계 서비스의 오픈 API를 사용하는 데이터를 요청하는 url
  req = urllib.request.Request(url)  #접속 요청 객체
  try:
    response = urllib.request.urlopen(req)  #서버에서 받은 응답을 저장하는 객체
    if response.getcode() == 200:
      print("[%s] Url Request Success" % datetime.datetime.now())
      return response.read().decode('utf-8')  #응답 형식 디코딩하여 반환하기
  except Exception as e:  #요청 처리되지 않은 예외사항 발생 시
    print(e)
    print("[%s] Error for URL : %s" % (datetime.datetime.now(), url))  #에러메시지 출력
    return None


# [CODE 2] : url 구성하여 데이터 요청  #응답으로 받은 월 데이터 반환
def getTourismStatsItem(yyyymm, national_code, ed_cd):  # ed_cd : 방한외래관광객 or 해외 출국
  service_url = 'http://openapi.tour.go.kr/openapi/service/EdrcntTourismStatsService/getEdrcntTourismStatsList'  
  parameters = "?_type=json&serviceKey=" + serviceKey  # 인증키
  parameters += "&YM=" + yyyymm
  parameters += "&NAT_CD=" + national_code
  parameters += "&ED_CD=" + ed_cd
  url = service_url + parameters

  retData = getRequestUrl(url)  # [CODE 1]

  #print(url)  #액세스 거부 여부 확인용 출력

  if (retData == None):
    return None
  else:
    return json.loads(retData)


# [CODE 3]
def getTourismStatsService(nat_cd, ed_cd, nStartYear, nEndYear):
  jsonResult = []
  result = []
  natName = ''
  dataEND = "{0}{1:0>2}".format(str(nEndYear), str(12))  # 데이터 끝 초기화
  isDataEnd = 0  # 데이터 끝 확인용 flag 초기화

  for year in range(nStartYear, nEndYear + 1):
    for month in range(1, 13):
      if (isDataEnd == 1): break  # 데이터 끝 flag 설정되어있으면 작업 중지.
      yyyymm = "{0}{1:0>2}".format(str(year), str(month))
      jsonData = getTourismStatsItem(yyyymm, nat_cd, ed_cd)  # [CODE 2]

      if (jsonData['response']['header']['resultMsg'] == 'OK'):
        # 입력된 범위까지 수집하지 않았지만, 더이상 제공되는 데이터가 없는 마지막 항목인 경우 -------------------
        if jsonData['response']['body']['items'] == '':
          isDataEnd = 1  # 데이터 끝 flag 설정
          dataEND = "{0}{1:0>2}".format(str(year), str(month - 1))
          print("데이터 없음.... \n 제공되는 통계 데이터는 %s년 %s월까지입니다." % (str(year), str(month - 1)))  #jsonData 출력하여 확인하기
          break
          # jsonData를 출력하여 확인......................................................
        print(json.dumps(jsonData, indent=4,sort_keys=True, ensure_ascii=False))
        natName = jsonData['response']['body']['items']['item']['natKorNm']   #수집한 국가 이름 데이터
        natName = natName.replace(' ', '')
        num = jsonData['response']['body']['items']['item']['num']  #수집한 방문객 수 데이터
        ed = jsonData['response']['body']['items']['item']['ed']  #수집한 출입국 구분 데이터
        print('[ %s_%s : %s ]' % (natName, yyyymm, num))
        print('----------------------------------------------------------------------')
        jsonResult.append({'nat_name': natName, 'nat_cd': nat_cd,
                           'yyyymm': yyyymm, 'visit_cnt': num})
        result.append([natName, nat_cd, yyyymm, num])

  return (jsonResult, result, natName, ed, dataEND)


# [CODE 0]
def main():
  jsonResult = []
  result = []
  natName = ''
  print('<< 국내 입국한 외국인의 통계 데이터를 수집합니다.>>')
  nat_cd = input('국가 코드를 입력하세요(중국: 112 / 일본: 130 / 미국: 275) : ')  #데이터 수집할 국가 코드 입력
  nStartYear = int(input('데이터륾 몇년부터 수집할까요?(ex.2017) '))  #데이터 수집할 시작 연도 입력
  nEndYear = int(input('데이터륾 몇년까지 수집할까요?(ex.2018) '))  #데이터 수집할 마지막 연도 입력
  ed_cd = 'E'  #E:방한외래관광객, D:해외 출국

  jsonResult, result, natName, ed, dataEND = getTourismStatsService(nat_cd, ed_cd, nStartYear, nEndYear)

  if (natName == ''):
    print('데이터가 전달되지 않았습니다. 공공데이터포털의 서비스 상태를 확인하시기 바랍니다.')
  else :
    # 파일 저장 : json 파일
    with open('./%s_%s_%d_%s.json' % (natName, ed, nStartYear, dataEND), 'w', encoding='utf-8') as outfile:
      jsonFile = json.dumps(jsonResult, indent=4, sort_keys=True, ensure_ascii=False)   #json 형식으로 변환
      outfile.write(jsonFile)
    # 파일 저장 : csv
    columns = ["입국자국가", "국가코드", "입국연월", "입국자 수"]
    result_df = pd.DataFrame(result, columns=columns)
    result_df.to_csv('./%s_%s_%d_%s.csv' % (natName, ed, nStartYear, dataEND), index=False, encoding='cp949')


if __name__ == '__main__':

  main()
