import urllib2 as urllib
import ujson as json
import numpy as np
#import json
from join import *
import os
# import pycurl
# from StringIO import StringIO
import sys
import time
from multiprocessing.dummy import Pool

threadnum = 20

#def ans.append(path):
#	#print path
#	ans.append(path)

urlcache = dict()
debug = False
pool = Pool(threadnum)

def urlrequest(url, first=False):
	if debug:
		return json.loads(urllib.urlopen(url).read())
	if first:
		res = urllib.urlopen(url).read()
		if not urlcache.has_key(url):
			urlcache[url] = res
		elif urlcache[url] != res:
			urlcache.clear()
			urlcache[url] = res
		return json.loads(res)
	else:
		if not urlcache.has_key(url):
			res = urllib.urlopen(url).read()
			urlcache[url] = res
			return json.loads(res)
		else:
			return json.loads(urlcache[url])

def getPaperJson(id, urlAttributes):
	url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=Id=%d&count=1000&attributes=%s&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%(id,urlAttributes)
	result = urlrequest(url)
	return result['entities'][0]

def getPaperJsonList(idList, urlAttributes):
	if idList == []:
		return []
	now = time.time()
	PaperJsonList = []
	poolResult = []
	L = 0
	expr = ''
	for id in idList:
		if expr == '':
			expr = 'Id=%d'%id
			L = len(expr)
		elif L + len(str(id)) + 8 <= 1800:
			expr = 'Or(%s,Id=%d)'%(expr,id)
			L += len(str(id)) + 8
		else:
			url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=%s&count=1000&attributes=%s&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%(expr,urlAttributes)
			poolResult.append(pool.apply_async(lambda url:urlrequest(url)['entities'], (url, )))

			expr = 'Id=%d'%id
			L = len(expr)

	url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=%s&count=1000&attributes=%s&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%(expr,urlAttributes)
	#print url
	poolResult.append(pool.apply_async(lambda url:urlrequest(url)['entities'], (url, )))

	#for result in poolResult:
	#	JsonList = result.get()
	#	for aJson in JsonList:
	#		PaperJsonList.append(aJson)
	PaperJsonList = [aJson for result in poolResult for aJson in result.get()]

	print 'getPaperJsonList time =', time.time() - now
	return PaperJsonList

def getAuthorPaperList(auidList, urlAttributes):
	if auidList == []:
		return []
	now = time.time()
	authorPaperList = []
	poolResult = []
	L = 0
	expr = ''
	for auid in auidList:
		if expr == '':
			expr = 'Composite(AA.AuId=%d)'%auid
			L = len(expr)
		elif L + len(str(auid)) + 24 <= 1800:
			expr = 'Or(%s,Composite(AA.AuId=%d))'%(expr,auid)
			L += len(str(auid)) + 24
		else:
			url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=%s&count=100000&attributes=%s&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%(expr,urlAttributes)
			poolResult.append(pool.apply_async(lambda url:urlrequest(url)['entities'], (url, )))

			expr = 'Composite(AA.AuId=%d)'%auid
			L = len(expr)

	url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=%s&count=100000&attributes=%s&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%(expr,urlAttributes)
	poolResult.append(pool.apply_async(lambda url:urlrequest(url)['entities'], (url, )))

	#for result in poolResult:
	#	paperList = result.get()
	#	for aPaper in paperList:
	#		authorPaperList.append(aPaper)
	authorPaperList = [aPaper for result in poolResult for aPaper in result.get()]

	print 'getAuthorPaperList time =', time.time() - now
	return authorPaperList

#def join(l1, l2): # join two sorted list
#	n1 = len(l1)
#	n2 = len(l2)
#	#l1.sort()
#	#l2.sort()
#	p1 = 0
#	p2 = 0
#	ret = []
#	while p1 < n1 and p2 < n2:
#		if l1[p1] < l2[p2]:
#			p1 += 1
#		elif l1[p1] > l2[p2]:
#			p2 += 1
#		else:
#			ret.append(l1[p1])
#			p1 += 1
#			p2 += 1
#	return ret

def query_Id_Id_big(id1, id2, json1, json2):
	#sys.stderr.write('query_Id_Id ' + str(id1) + ' ' + str(id2) + '\n')
	print 'query_Id_Id_big', id1, id2
	ans = []

	#print json1

	#json1 = getPaperJson(id1, 'RId,F.FId,J.JId,C.CId,AA.AuId')
	#json2 = getPaperJson(id2, 'F.FId,J.JId,C.CId,AA.AuId')
	#print json1['RId']
	#print json2

	now = time.time()
	url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=And(RId=%d,CC>0)&count=50000&orderby=CC:desc&attributes=Id,F.FId,J.JId,C.CId,AA.AuId&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%id2
	Id2citedResult = pool.apply_async(lambda url:urlrequest(url)['entities'], (url, ))
	if json1.has_key('RId'):
		urlAttributes = 'Id,RId'
		if json2.has_key('F'):
			urlAttributes += ',F.FId'
		if json2.has_key('J'):
			urlAttributes += ',J.JId'
		if json2.has_key('C'):
			urlAttributes += ',C.CId'
		if json2.has_key('AA'):
			urlAttributes += ',AA.AuId'
	#	id1CitePapersInfoResult = pool.map_async(lambda x:getPaperJson(x, urlAttributes), json1['RId'])
		#print json1
		id1CitePapersInfo = getPaperJsonList(json1['RId'], urlAttributes)
	#print 'time use2: ', time.time() - now
	# =========== 1-hop =========== 

	# Id-Id
	if json1.has_key('RId') and id2 in json1['RId']:
		ans.append([id1, id2])

	# =========== 2-hop =========== 

	# Id-F.FId-Id
	if json1.has_key('F'):
		FIdList1 = map(lambda x:x['FId'], json1['F'])
		FIdList1.sort()
	if json2.has_key('F'):
		FIdList2 = map(lambda x:x['FId'], json2['F'])
		FIdList2.sort()		
	if json1.has_key('F') and json2.has_key('F'):
		jointFIdList = join(FIdList1, FIdList2)
		map(lambda x: ans.append([id1, x, id2]), jointFIdList)
			

	# Id-J.JId-Id
	if json1.has_key('J') and json2.has_key('J') and json1['J']['JId'] == json2['J']['JId']:
		ans.append([id1, json1['J']['JId'], id2])

	# Id-C.CId-Id
	if json1.has_key('C') and json2.has_key('C') and json1['C']['CId'] == json2['C']['CId']:
		ans.append([id1, json1['C']['CId'], id2])

	# Id-AA.AuId-Id
	if json1.has_key('AA'):
		AuIdList1 = map(lambda x:x['AuId'], json1['AA'])
		AuIdList1.sort()
	if json2.has_key('AA'):
		AuIdList2 = map(lambda x:x['AuId'], json2['AA'])
		AuIdList2.sort()
	if json1.has_key('AA') and json2.has_key('AA'):
		jointAuIdList = join(AuIdList1, AuIdList2)
		map(lambda x: ans.append([id1, x, id2]), jointAuIdList)
			

	# Id-Id-Id
	# TODO 
	Id2cited = Id2citedResult.get()
	if json1.has_key('RId'):
		RIdList = json1['RId']
		Id2citedList = map(lambda x:x['Id'], Id2cited)
		RIdList.sort()
		Id2citedList.sort()
		jointRIdList = join(RIdList, Id2citedList)
		map(lambda x: ans.append([id1, x, id2]), jointRIdList)
			

	# =========== 3-hop =========== 

	# Id-*-Id-Id
	if len(Id2cited) != 0:

		now = time.time()
		poolResult = []
		if json1.has_key('F'):
			for FId in FIdList1:
				url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=And(RId=%d,Composite(F.FId=%d))&count=200000&attributes=Id&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%(id2, FId)
				poolResult.append(pool.apply_async(lambda url:urlrequest(url)['entities'], (url, )))
		if json1.has_key('J'):
			url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=And(RId=%d,Composite(J.JId=%d))&count=200000&attributes=Id&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%(id2, json1['J']['JId'])
			poolResult.append(pool.apply_async(lambda url:urlrequest(url)['entities'], (url, )))
		if json1.has_key('C'):
			url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=And(RId=%d,Composite(C.CId=%d))&count=200000&attributes=Id&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%(id2, json1['C']['CId'])
			poolResult.append(pool.apply_async(lambda url:urlrequest(url)['entities'], (url, )))
		if json1.has_key('AA'):
			for AuId in AuIdList1:
				url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=And(RId=%d,Composite(AA.AuId=%d))&count=200000&attributes=Id&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%(id2, AuId)
				poolResult.append(pool.apply_async(lambda url:urlrequest(url)['entities'], (url, )))
		#pool.close()
		#pool.join()
		#print 'time use3: ', time.time() - now

		idx = 0

		# Id-F.FId-Id-Id
		if json1.has_key('F'):
			for FId in FIdList1:
				comPaperList = poolResult[idx].get()
				idx += 1
				map(lambda x: ans.append([id1, FId, x['Id'], id2]), comPaperList)
					

		# Id-J.JId-Id-Id
		if json1.has_key('J'):
			JId = json1['J']['JId']
			comPaperList = poolResult[idx].get()
			idx += 1
			map(lambda x: ans.append([id1, JId, x['Id'], id2]), comPaperList)
				

		# Id-C.CId-Id-Id
		if json1.has_key('C'):
			CId = json1['C']['CId']
			comPaperList = poolResult[idx].get()
			idx += 1
			map(lambda x: ans.append([id1, CId, x['Id'], id2]), comPaperList)
				
		
		# Id-AA.AuId-Id-Id
		if json1.has_key('AA'):
			for AuId in AuIdList1:
				comPaperList = poolResult[idx].get()
				idx += 1
				map(lambda x: ans.append([id1, AuId, x['Id'], id2]), comPaperList)
					

	# Id-Id-*-Id
	if json1.has_key('RId'):
		#id1CitePapersInfo = id1CitePapersInfoResult.get()
		# Id-Id-F.FId-Id
		if json2.has_key('F'):
			for id1CitePaper in id1CitePapersInfo:
				if id1CitePaper.has_key('F'):
					FIdListTmp = map(lambda x:x['FId'], id1CitePaper['F'])
					FIdListTmp.sort()
					jointFIdList = join(FIdListTmp, FIdList2)
					map(lambda x: ans.append([id1, id1CitePaper['Id'], x, id2]), jointFIdList)
						

		# Id-Id-J.JId-Id
		if json2.has_key('J'):
			for id1CitePaper in id1CitePapersInfo:
				if id1CitePaper.has_key('J') and id1CitePaper['J']['JId'] == json2['J']['JId']:
					ans.append([id1, id1CitePaper['Id'], json2['J']['JId'], id2])

		# Id-Id-C.CId-Id
		if json2.has_key('C'):
			for id1CitePaper in id1CitePapersInfo:
				if id1CitePaper.has_key('C') and id1CitePaper['C']['CId'] == json2['C']['CId']:
					ans.append([id1, id1CitePaper['Id'], json2['C']['CId'], id2])

		# Id-Id-AA.AuId-Id
		if json2.has_key('AA'):
			for id1CitePaper in id1CitePapersInfo:
				if id1CitePaper.has_key('AA'):
					AuIdListTmp = map(lambda x:x['AuId'], id1CitePaper['AA'])
					AuIdListTmp.sort()
					jointAuIdList = join(AuIdListTmp, AuIdList2)
					map(lambda x: ans.append([id1, id1CitePaper['Id'], x, id2]), jointAuIdList)
						

		# Id-Id-Id-Id
		tmp = len(ans)
		for id1CitePaper in id1CitePapersInfo:
			if id1CitePaper.has_key('RId'):
				RIdListTmp = id1CitePaper['RId']
				RIdListTmp.sort()
				jointRIdList = join(RIdListTmp, Id2citedList)
				map(lambda x: ans.append([id1, id1CitePaper['Id'], x, id2]), jointRIdList)
					
		#print 'len(Id-Id-Id-Id) =', len(ans)-tmp

	# return ans
	return ans

def query_Id_Id_small(id1, id2, json1, json2):
	#sys.stderr.write('query_Id_Id ' + str(id1) + ' ' + str(id2) + '\n')
	print 'query_Id_Id_small', id1, id2
	ans = []

	#print json1

	#json1 = getPaperJson(id1, 'RId,F.FId,J.JId,C.CId,AA.AuId')
	#json2 = getPaperJson(id2, 'F.FId,J.JId,C.CId,AA.AuId')
	#print json1['RId']
	#print json2
	
	now = time.time()
	url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=RId=%d&count=50000&orderby=CC:desc&attributes=Id,F.FId,J.JId,C.CId,AA.AuId&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%id2
	Id2citedResult = pool.apply_async(lambda url:urlrequest(url)['entities'], (url,))
	if json1.has_key('RId'):
		urlAttributes = 'Id,RId'
		if json2.has_key('F'):
			urlAttributes += ',F.FId'
		if json2.has_key('J'):
			urlAttributes += ',J.JId'
		if json2.has_key('C'):
			urlAttributes += ',C.CId'
		if json2.has_key('AA'):
			urlAttributes += ',AA.AuId'
	#	id1CitePapersInfoResult = pool.map_async(lambda x:getPaperJson(x, urlAttributes), json1['RId'])
		id1CitePapersInfo = getPaperJsonList(json1['RId'], urlAttributes)
	#print 'time use2: ', time.time() - now

	# =========== 1-hop =========== 

	# Id-Id
	if json1.has_key('RId') and id2 in json1['RId']:
		ans.append([id1, id2])

	# =========== 2-hop =========== 

	# Id-F.FId-Id
	if json1.has_key('F'):
		FIdList1 = map(lambda x:x['FId'], json1['F'])
		FIdList1.sort()
	if json2.has_key('F'):
		FIdList2 = map(lambda x:x['FId'], json2['F'])
		FIdList2.sort()		
	if json1.has_key('F') and json2.has_key('F'):
		jointFIdList = join(FIdList1, FIdList2)
		map(lambda x: ans.append([id1, x, id2]), jointFIdList)
			

	# Id-J.JId-Id
	if json1.has_key('J') and json2.has_key('J') and json1['J']['JId'] == json2['J']['JId']:
		ans.append([id1, json1['J']['JId'], id2])

	# Id-C.CId-Id
	if json1.has_key('C') and json2.has_key('C') and json1['C']['CId'] == json2['C']['CId']:
		ans.append([id1, json1['C']['CId'], id2])

	# Id-AA.AuId-Id
	if json1.has_key('AA'):
		AuIdList1 = map(lambda x:x['AuId'], json1['AA'])
		AuIdList1.sort()
	if json2.has_key('AA'):
		AuIdList2 = map(lambda x:x['AuId'], json2['AA'])
		AuIdList2.sort()
	if json1.has_key('AA') and json2.has_key('AA'):
		jointAuIdList = join(AuIdList1, AuIdList2)
		map(lambda x: ans.append([id1, x, id2]), jointAuIdList)
			

	# Id-Id-Id
	Id2cited = Id2citedResult.get()
	if json1.has_key('RId'):
		RIdList = json1['RId']
		Id2citedList = map(lambda x:x['Id'], Id2cited)
		RIdList.sort()
		Id2citedList.sort()
		jointRIdList = join(RIdList, Id2citedList)
		map(lambda x: ans.append([id1, x, id2]), jointRIdList)
			

	# =========== 3-hop =========== 

	# Id-*-Id-Id
	if len(Id2cited) != 0:
		# Id-F.FId-Id-Id
		if json1.has_key('F'):
			for paper in Id2cited:
				if paper.has_key('F'):
					for F_element in paper['F']:
						if F_element['FId'] in FIdList1:
							ans.append([id1, F_element['FId'], paper['Id'], id2])

		# Id-J.JId-Id-Id
		if json1.has_key('J'):
			for paper in Id2cited:
				if paper.has_key('J') and paper['J']['JId'] == json1['J']['JId']:
					ans.append([id1, json1['J']['JId'], paper['Id'], id2])

		# Id-C.CId-Id-Id
		if json1.has_key('C'):
			for paper in Id2cited:
				if paper.has_key('C') and paper['C']['CId'] == json1['C']['CId']:
					ans.append([id1, json1['C']['CId'], paper['Id'], id2])
		
		# Id-AA.AuId-Id-Id
		if json1.has_key('AA'):
			for paper in Id2cited:
				if paper.has_key('AA'):
					for AA_element in paper['AA']:
						if AA_element['AuId'] in AuIdList1:
							ans.append([id1, AA_element['AuId'], paper['Id'], id2])

	# Id-Id-*-Id
	if json1.has_key('RId'):
		#id1CitePapersInfo = id1CitePapersInfoResult.get()
		# Id-Id-F.FId-Id
		if json2.has_key('F'):
			for id1CitePaper in id1CitePapersInfo:
				if id1CitePaper.has_key('F'):
					FIdListTmp = map(lambda x:x['FId'], id1CitePaper['F'])
					FIdListTmp.sort()
					jointFIdList = join(FIdListTmp, FIdList2)
					map(lambda x: ans.append([id1, id1CitePaper['Id'], x, id2]), jointFIdList)
						

		# Id-Id-J.JId-Id
		if json2.has_key('J'):
			for id1CitePaper in id1CitePapersInfo:
				if id1CitePaper.has_key('J') and id1CitePaper['J']['JId'] == json2['J']['JId']:
					ans.append([id1, id1CitePaper['Id'], json2['J']['JId'], id2])

		# Id-Id-C.CId-Id
		if json2.has_key('C'):
			for id1CitePaper in id1CitePapersInfo:
				if id1CitePaper.has_key('C') and id1CitePaper['C']['CId'] == json2['C']['CId']:
					ans.append([id1, id1CitePaper['Id'], json2['C']['CId'], id2])

		# Id-Id-AA.AuId-Id
		if json2.has_key('AA'):
			for id1CitePaper in id1CitePapersInfo:
				if id1CitePaper.has_key('AA'):
					AuIdListTmp = map(lambda x:x['AuId'], id1CitePaper['AA'])
					AuIdListTmp.sort()
					jointAuIdList = join(AuIdListTmp, AuIdList2)
					map(lambda x: ans.append([id1, id1CitePaper['Id'], x, id2]), jointAuIdList)
						

		# Id-Id-Id-Id
		tmp = len(ans)
		for id1CitePaper in id1CitePapersInfo:
			if id1CitePaper.has_key('RId'):
				RIdListTmp = id1CitePaper['RId']
				RIdListTmp.sort()
				jointRIdList = join(RIdListTmp, Id2citedList)
				map(lambda x: ans.append([id1, id1CitePaper['Id'], x, id2]), jointRIdList)
					
		#print 'len(Id-Id-Id-Id) =', len(ans)-tmp

	# return ans
	return ans

def query_AuId_Id(auId1, id2, json1, json2):
	#sys.stderr.write('query_AuId_Id ' + str(auId1) + ' ' + str(id2) + '\n')
	print 'query_AuId_Id', auId1, id2
	ans = []
	
	now = time.time()
	
	url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=RId=%d&count=100000&orderby=CC:desc&attributes=Id&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%id2
	Id2citedResult = pool.apply_async(lambda url:urlrequest(url)['entities'], (url,))

	#now = time.time()
	#json2 = getPaperJson(id2, 'F.FId,J.JId,C.CId,AA.AuId,AA.AfId')
	#print 'time use2: ', time.time() - now
	#url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=Composite(AA.AuId=%d)&count=20000&attributes=Id,RId,F.FId,J.JId,C.CId,AA.AuId&orderby=D:desc&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%auId1
	#json1 = json.loads((urllib.urlopen(url)).read())['entities']

	# =========== 1-hop =========== 

	# AuId-Id
	for paper in json1:
		if paper['Id'] == id2:
			ans.append([auId1, id2])
			break


	# =========== 2-hop =========== 

	# AuId-Id-Id
	for paper in json1:
		if paper.has_key('RId') and (id2 in paper['RId']):
			ans.append([auId1, paper['Id'], id2])

	# =========== 3-hop =========== 

	# AuId-Id-F.FId-Id
	if json2.has_key('F'):
		FIdList2 = map(lambda x:x['FId'], json2['F'])
		FIdList2.sort()
		for paper in json1:
			if paper.has_key('F'):
				FIdListTmp = map(lambda x:x['FId'], paper['F'])
				FIdListTmp.sort()
				jointFIdList = join(FIdListTmp, FIdList2)
				map(lambda x: ans.append([auId1, paper['Id'], x, id2]), jointFIdList)
					

	# AuId-Id-C.CId-Id
	if json2.has_key('C'):
		CId2 = json2['C']['CId']
		for paper in json1:
			if paper.has_key('C') and paper['C']['CId'] == CId2:
				ans.append([auId1, paper['Id'], CId2, id2])

	# AuId-Id-J.JId-Id
	if json2.has_key('J'):
		JId2 = json2['J']['JId']
		for paper in json1:
			if paper.has_key('J') and paper['J']['JId'] == JId2:
				ans.append([auId1, paper['Id'], JId2, id2])

	# AuId-Id-AA.AuId-Id
	if json2.has_key('AA'):
		AuIdList2 = map(lambda x:x['AuId'], json2['AA'])
		AuIdList2.sort()
		for paper in json1:
			if paper.has_key('AA'):
				AuIdListTmp = map(lambda x:x['AuId'], paper['AA'])
				AuIdListTmp.sort()
				jointAuIdList = join(AuIdListTmp, AuIdList2)
				map(lambda x: ans.append([auId1, paper['Id'], x, id2]), jointAuIdList)
	print 'AuId-Id-AuId-Id finished time =', time.time() - now	

	# AuId-Id-Id-Id
	#now = time.time()
	Id2cited = Id2citedResult.get()
	print 'Id2cited geted time =', time.time() - now
	if len(Id2cited) > 0:
		Id2citedList = map(lambda x:x['Id'], Id2cited)
		Id2citedList.sort()
		for paper in json1:
			if paper.has_key('RId'):
				RIdListTmp = paper['RId']
				RIdListTmp.sort()
				jointRIdList = join(RIdListTmp, Id2citedList)
				map(lambda x: ans.append([auId1, paper['Id'], x, id2]), jointRIdList)
					

	# AuId-AA.AFId-AA.AuId-Id
	AFIdSet1 = set()
	for paper in json1:
		if paper.has_key('AA'):
			for author in paper['AA']:
				if author['AuId'] == auId1 and author.has_key('AfId'):
					AFIdSet1.add(author['AfId'])
	if len(AFIdSet1) > 0 and json2.has_key('AA'):
		authorPaperList = getAuthorPaperList(map(lambda x:x['AuId'], json2['AA']), 'AA.AuId,AA.AfId')
		authorSet2 = set()
		map(lambda x:authorSet2.add(x['AuId']), json2['AA'])
		uniqueSet = set()
		for paper in authorPaperList:
			if paper.has_key('AA'):
				for author in paper['AA']:
					auId2 = author['AuId']
					if (auId2 in authorSet2) and author.has_key('AfId') and (author['AfId'] in AFIdSet1) and not((author['AfId'], auId2) in uniqueSet):
						ans.append([auId1, author['AfId'], auId2, id2])
						uniqueSet.add((author['AfId'], auId2))
	print 'AuId-AfId-AuId-Id finished time =', time.time() - now

	#AFIdSet1 = set()
	#for paper in json1:
	#	if paper.has_key('AA'):
	#		for author in paper['AA']:
	#			if author['AuId'] == auId1 and author.has_key('AfId'):
	#				AFIdSet1.add(author['AfId'])
	#if json2.has_key('AA'):
	#	for author in json2['AA']:
	#		if author.has_key('AfId'):
	#			if author['AfId'] in AFIdSet1:
	#				ans.append([auId1, author['AfId'], author['AuId'], id2])
	
	return ans

def query_Id_AuId(id1, auId2, json1, json2):
	#sys.stderr.write('query_AuId_Id ' + str(id1) + ' ' + str(auId2) + '\n')
	print 'query_Id_AuId', id1, auId2
	ans = []
	
	#now = time.time()
	#json1 = getPaperJson(id1, 'RId,F.FId,J.JId,C.CId,AA.AuId,AA.AfId')
	#print 'time use: ', time.time() - now	
	#now = time.time()
	#url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=Composite(AA.AuId=%d)&count=20000&attributes=Id,F.FId,J.JId,C.CId,AA.AuId&orderby=D:asc&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%auId2
	#json2 = json.loads((urllib.urlopen(url)).read())['entities']

	paperIdList = map(lambda x:x['Id'], json2)
	paperIdList.sort()

	# =========== 1-hop ===========

	# Id-AuId
	if json1.has_key('AA') and (auId2 in map(lambda x:x['AuId'], json1['AA'])):
		ans.append([id1, auId2])

	# =========== 2-hop ===========

	# Id-Id-AuId
	if json1.has_key('RId'):
		RIdList = json1['RId']
		RIdList.sort()
		jointRIdList = join(paperIdList, RIdList)
		map(lambda x: ans.append([id1, x, auId2]), jointRIdList)
			

	# =========== 3-hop ===========

	# Id-F.FId-Id-AuId
	if json1.has_key('F'):
		FIdList1 = map(lambda x:x['FId'], json1['F'])
		FIdList1.sort()
		for paper in json2:
			if paper.has_key('F'):
				FIdListTmp = map(lambda x:x['FId'], paper['F'])
				FIdListTmp.sort()
				jointFIdList = join(FIdListTmp, FIdList1)
				map(lambda x: ans.append([id1, x, paper['Id'], auId2]), jointFIdList)

	# Id-C.CId-Id-AuId
	if json1.has_key('C'):
		CId1 = json1['C']['CId']
		for paper in json2:
			if paper.has_key('C') and paper['C']['CId'] == CId1:
				ans.append([id1, CId1, paper['Id'], auId2])

	# Id-J.JId-Id-AuId
	if json1.has_key('J'):
		JId1 = json1['J']['JId']
		for paper in json2:
			if paper.has_key('J') and paper['J']['JId'] == JId1:
				ans.append([id1, JId1, paper['Id'], auId2])

	# Id-AA.AuId-Id-AuId
	if json1.has_key('AA'):
		AuIdList1 = map(lambda x:x['AuId'], json1['AA'])
		AuIdList1.sort()
		for paper in json2:
			if paper.has_key('AA'):
				AuIdListTmp = map(lambda x:x['AuId'], paper['AA'])
				AuIdListTmp.sort()
				jointAuIdList = join(AuIdListTmp, AuIdList1)
				map(lambda x: ans.append([id1, x, paper['Id'], auId2]), jointAuIdList)
					

	# Id-Id-Id-AuId
	if json1.has_key('RId'):
		citePaperInfoResults = pool.map_async(lambda x:getPaperJson(x, 'RId,Id'), RIdList)
		#pool.close()
		#pool.join()
		citePaperInfos = citePaperInfoResults.get()
		for citePaperInfo in citePaperInfos:
			if citePaperInfo.has_key('RId'):
				RIdListTmp = citePaperInfo['RId']
				RIdListTmp.sort()
				jointRIdList = join(RIdListTmp, paperIdList)
				map(lambda x: ans.append([id1, citePaperInfo['Id'], x, auId2]), jointRIdList)

	# Id-AA.AuId-AA.AfId-AuId
	AFIdSet2 = set()
	for paper in json2:
		if paper.has_key('AA'):
			for author in paper['AA']:
				if author['AuId'] == auId2 and author.has_key('AfId'):
					AFIdSet2.add(author['AfId'])
	if len(AFIdSet2) > 0 and json1.has_key('AA'):
		authorPaperList = getAuthorPaperList(map(lambda x:x['AuId'], json1['AA']), 'AA.AuId,AA.AfId')
		authorSet1 = set()
		map(lambda x: authorSet1.add(x['AuId']), json1['AA'])
		uniqueSet = set()
		for paper in authorPaperList:
			if paper.has_key('AA'):
				for author in paper['AA']:
					auId1 = author['AuId']
					if (auId1 in authorSet1) and author.has_key('AfId') and (author['AfId'] in AFIdSet2) and not((auId1, author['AfId']) in uniqueSet):
						ans.append([id1, auId1, author['AfId'], auId2])
						uniqueSet.add((auId1, author['AfId']))

	#AFIdSet2 = set()
	#for paper in json2:
	#	if paper.has_key('AA'):
	#		for author in paper['AA']:
	#			if author['AuId'] == auId2 and author.has_key('AfId'):
	#				AFIdSet2.add(author['AfId'])
	#if json1.has_key('AA'):
	#	for author in json1['AA']:
	#		if author.has_key('AfId'):
	#			if author['AfId'] in AFIdSet2:
	#				ans.append([id1, author['AuId'], author['AfId'], auId2])

	#print 'time use2: ', time.time() - now
	return ans

def query_AuId_AuId(auId1, auId2, json1, json2):
	sys.stderr.write('query_AuId_AuId ' + str(auId1) + ' ' + str(auId2) + '\n')
	ans = []

	# =========== 2-hop ===========
	#print len(json1), len(json2)
	# print json2
	AFIdSet1 = set()
	IdList1 = []
	for paper1 in json1:
		if paper1.has_key('AA'):
			for i in paper1['AA']:
				if i.has_key('AfId') and i['AuId'] == auId1:
					AFIdSet1.add(i['AfId'])
		if paper1.has_key('Id'):
			IdList1.append(paper1['Id'])
	IdList1.sort()

	AFIdSet2 = set()
	IdList2 = []
	for paper2 in json2:
		if paper2.has_key('AA'):
			for i in paper2['AA']:
				if i.has_key('AfId') and i['AuId'] == auId2:
					AFIdSet2.add(i['AfId'])
		if paper2.has_key('Id'):
			IdList2.append(paper2['Id'])
	IdList2.sort()

	#AuId-AFId-AuId
	if len(AFIdSet1)>0 and len(AFIdSet2)>0:
		# AFIdList1.sort()
		# AFIdList2.sort()
		# jointAFIdList = join(AFIdList1, AFIdList2)
		# jointAFIdList = np.intersect1d(AFIdList1, AFIdList2)
		jointAFIdSet = AFIdSet1.intersection(AFIdSet2)
		# for AFId in jointAFIdList:
		map(lambda x: ans.append([auId1, x, auId2]), jointAFIdSet)
	#print len(ans)
	#AuId-Id-AuId
	if len(IdList1)>0 and len(IdList2)>0:
		jointIdList = join(IdList1, IdList2)
		map(lambda x: ans.append([auId1, x, auId2]), jointIdList)
	#print len(ans)
	# =========== 3-hop ===========

	# AuId-Id-Id-AuId
	for paper1 in json1:
		if paper1.has_key('RId'):
			RIdList = paper1['RId']
			RIdList.sort()
			jointList = join(RIdList, IdList2)
			map(lambda x: ans.append([auId1, paper1['Id'], x, auId2]), jointList)
			# paper1['RId'] = dict(zip(paper1['RId'], range(len(paper1['RId']))))
			# for paper2 in json2:
			# 	if paper2['Id'] in paper1['RId']:
			# 		ans.append([auId1, paper1['Id'], paper2['Id'], auId2])
	#print len(ans)
	return ans

def query(id1, id2):
	now = time.time()
	#url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=Composite(AA.AuId=%d)&count=20000&attributes=Id,RId,F.FId,J.JId,C.CId,AA.AuId,AA.AfId&orderby=D:desc&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%id1
	#json1 = json.loads((urllib.urlopen(url)).read())['entities']
	#url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=Composite(AA.AuId=%d)&count=20000&attributes=Id,F.FId,J.JId,C.CId,AA.AuId,AA.AfId&orderby=D:asc&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%id2
	#json2 = json.loads((urllib.urlopen(url)).read())['entities']
	#print 'time use: ', time.time() - now
	#url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=Composite(AA.AuId=%d)&count=1&attributes=Id,AA.AuId,AA.AfId&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%id1
	#json1 = (json.loads((urllib.urlopen(url)).read()))['entities']
	#url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=Composite(AA.AuId=%d)&count=1&attributes=Id,AA.AuId,AA.AfId&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%id2
	#json2 = (json.loads((urllib.urlopen(url)).read()))['entities']

	json1 = []
	json2 = []
	paperJson1 = []
	paperJson2 = []
	url = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=Or(Or(Or(Composite(AA.AuId=%d),Composite(AA.AuId=%d)),Id=%d),Id=%d)&count=40000&attributes=Id,RId,F.FId,J.JId,C.CId,AA.AuId,AA.AfId,CC&orderby=D:desc&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%(id1,id2,id1,id2)
	#print type(url)
	#mix = json.loads(urllib.urlopen(url).read())['entities']
	mix = urlrequest(url, True)['entities']
	print 'init get time =', time.time() - now
	#print mix
	for ele in mix:
		if ele.has_key('AA'):
			AuIdList = map(lambda x:x['AuId'], ele['AA'])
			if id1 in AuIdList:
				json1.append(ele)
			if id2 in AuIdList:
				json2.append(ele)
		if ele['Id'] == id1:
			paperJson1.append(ele)
		if ele['Id'] == id2:
			paperJson2.append(ele)
	#print paperJson1
	print 'init time =', time.time() - now

	#url1 = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=Composite(AA.AuId=%d)&count=20000&attributes=Id,RId,F.FId,J.JId,C.CId,AA.AuId,AA.AfId&orderby=D:desc&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%id1
	#url2 = 'https://oxfordhk.azure-api.net/academic/v1.0/evaluate?expr=Composite(AA.AuId=%d)&count=20000&attributes=Id,F.FId,J.JId,C.CId,AA.AuId,AA.AfId&orderby=D:asc&subscription-key=f7cc29509a8443c5b3a5e56b0e38b5a6'%id2
	#poolResult = []
	#pool = Pool(threadnum)
	#poolResult.append(pool.apply_async(lambda url: json.loads((urllib.urlopen(url)).read())['entities'], (url1,)))
	#poolResult.append(pool.apply_async(lambda url: json.loads((urllib.urlopen(url)).read())['entities'], (url2,)))
	#poolResult.append(pool.apply_async(getPaperJson, (id1, 'RId,F.FId,J.JId,C.CId,AA.AuId,AA.AfId')))
	#poolResult.append(pool.apply_async(getPaperJson, (id2, 'F.FId,J.JId,C.CId,AA.AuId,AA.AfId,CC')))
	#pool.close()
	#pool.join()
	#json1 = poolResult[0].get()
	#json2 = poolResult[1].get()
	#paperJson1 = poolResult[2].get()
	#paperJson2 = poolResult[3].get()
	# print len(json2)
	
	if json1 and json2:
		#afId1 = -1
		#afId2 = -1
		#for author in json1[0]['AA']:
		#	if author['AuId'] == id1 and author.has_key('AfId'):
		#		afId1 = author['AfId']
		#for author in json2[0]['AA']:
		#	if author['AuId'] == id2 and author.has_key('AfId'):
		#		afId2 = author['AfId']
		#return query_AuId_AuId(id1, id2, afId1, afId2)
		return query_AuId_AuId(id1, id2, json1, json2)
	elif json1:
		#afId1 = -1
		#for author in json1[0]['AA']:
		#	if author['AuId'] == id1 and author.has_key('AfId'):
		#		afId1 = author['AfId']
		#return query_AuId_Id(id1, id2, afId1)
		return query_AuId_Id(id1, id2, json1, paperJson2[0])
	elif json2:
		#afId2 = -1
		#for author in json2[0]['AA']:
		#	if author['AuId'] == id2 and author.has_key('AfId'):
		#		afId2 = author['AfId']
		#return query_Id_AuId(id1, id2, afId2)
		return query_Id_AuId(id1, id2, paperJson1[0], json2)
	else:
		paperJson1 = paperJson1[0]
		paperJson2 = paperJson2[0]
		if paperJson2.has_key('CC') and paperJson2['CC'] >= 50000:
			return query_Id_Id_big(id1, id2, paperJson1, paperJson2)
		else:
			return query_Id_Id_small(id1, id2, paperJson1, paperJson2)			

def main(id1, id2):
	#query(2140190241, 1514498087)
	#query(2140190241, 1490955312)
	#query(2126125555, 2153635508)
	#query(2126125555, 2060367530)
	#query(2140190241, 2121939561)
	#query(2175015405, 1514498087)
	#print query(2251253715,2180737804)
	#print len(query(2100837269, 621499171))
	print len(query(id1, id2))
	now = time.time()
	print len(query(id1, id2))
	#print len(query(2140619391,2044675247))
	print time.time() - now

if __name__ == '__main__':
    main(int(sys.argv[1]), int(sys.argv[2]))
