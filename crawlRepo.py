from config import *
import mysql.connector
import json


class crawlRepo:
    def __init__(self):
        True

    def insertEntity(self, entity, webSiteID):
        query = '''INSERT INTO crawlContent
            (
              webSiteID
             ,title
             ,company
             ,pureContent
             ,location
             ,skills
             ,workType
             ,minExperience
             ,price
             ,tags
             ,link
             ,minDegree
             ,lastCrawlDate
             ,expirationDate
            )
            VALUES
            (
             {webSiteID} 
             ,"{title}" 
             ,"{company}"
             ,"{pureContent}" 
             ,"{location}" 
             ,'{skills}' 
             ,'{workType}'
             ,"{minExperience}" 
             ,"{price}" 
             ,'{tags}'
             ,"{link}"
             ,"{minDegree}"
             ,NOW()
             ,"{expirationDate}"
            )
            ON DUPLICATE KEY 
            UPDATE 
            title="{title}",title="{title}",company="{company}",pureContent="{pureContent}",location="{location}",skills='{skills}',
            workType='{workType}',minExperience="{minExperience}",price="{price}",tags='{tags}',link="{link}",minDegree="{minDegree}",lastCrawlDate=NOW(),
            expirationDate="{expirationDate}"
            ;'''.format(webSiteID=webSiteID, title=entity['title'], company=entity['company'],
                        pureContent=entity['content'], location=entity['location'],
                        skills=json.dumps(entity['skills'], ensure_ascii=False),
                        workType=json.dumps(entity['work_type'], ensure_ascii=False),
                        minExperience=entity['minimum_experience'], price=entity['price'],
                        tags=json.dumps(entity['tags'], ensure_ascii=False), link=entity['url'],
                        minDegree=entity['minimum_degree'],expirationDate=entity['expiration_date'])
        return self.setResult(query)

    def setResult(self, query):
        res = False
        try:
            cnx = mysql.connector.connect(**dbConfig)
            cursor = cnx.cursor(buffered=True)
        except mysql.connector.Error as err:
            logging.error("Failed connect db: {}".format(err))
            return res
        try:
            cursor.execute(query)
            cnx.commit()
            res = True
        except mysql.connector.Error as err:
            logging.error("Failed Insert Result member: {}".format(err))
            res = False
        finally:
            cursor.close()
            cnx.close()
            return res

    def checkExistRecord(self, entity, webSiteID):
        response = False
        try:
            cnx = mysql.connector.connect(**dbConfig)
            cursor = cnx.cursor(buffered=True)
        except mysql.connector.Error as err:
            logging.error("Failed connect db: {}".format(err))
            return 'Error'
        try:
            query = '''
            SELECT
                ID
            FROM crawlContent
            WHERE link="{link}"
            '''.format(link=entity['url'])
            cursor.execute(query)
            if cursor.rowcount == 0:
                response = False  # Not Exist
            else:
                response = True  # Record Already Exist
        except mysql.connector.Error as err:
            logging.error("Failed check Exist: {}".format(err))
            response = 'Error'
        finally:
            cursor.close()
            cnx.close()
            return response

    def getRecordsBySkill(self, skill, paging_id=None, mode='next'):
        response = False
        try:
            cnx = mysql.connector.connect(**dbConfig)
            cursor = cnx.cursor(buffered=True)
        except mysql.connector.Error as err:
            logging.error("Failed connect db: {}".format(err))
            return 'Error'
        try:
            query = 'SELECT * FROM crawlContent WHERE skills REGEXP "{skill}" AND expirationDate > NOW()'.format(skill=skill)
            if paging_id:
                query += ' AND expirationDate {mode} "{paging_id}"'.format(mode=paging_mode[mode], paging_id=paging_id)
            query += ' ORDER BY expirationDate DESC'
            cursor.execute(query)
            if cursor.rowcount == 0:
                response = False  # Not Exist
            else:
                response = {
                    'feeds': [],
                    'is_next_page': False,
                    'next_max_id': False
                }
                records = cursor.fetchall()
                if len(records) > paging_limit:
                    response['is_next_page'] = True
                for item in records[:paging_limit]:
                    out = {
                        'ID': item[0],
                        'title': item[2],
                        'company': item[3],
                        'pureContent': item[4],
                        'location': item[5],
                        'skills': json.loads(item[6]),
                        'workType': json.loads(item[7]),
                        'minExperience': item[8],
                        'price': item[9],
                        'tags': json.loads(item[10]),
                        'link': item[11],
                        'minDegree': item[12],
                        'expirationDate': item[14],
                    }
                    response['feeds'].append(out)
                if response['is_next_page']:
                    response['next_max_id'] = response['feeds'][-1]['expirationDate']

        except mysql.connector.Error as err:
            logging.error("Failed get Record: {}".format(err))
            response = 'Error'
        except Exception as err:
            logging.error("Failed get Record: {}".format(err))
            response = 'Error'
        finally:
            cursor.close()
            cnx.close()
            return response

    def getRecordExpirationNull(self):
        response = False
        try:
            cnx = mysql.connector.connect(**dbConfig)
            cursor = cnx.cursor(buffered=True)
        except mysql.connector.Error as err:
            logging.error("Failed connect db: {}".format(err))
            return 'Error'
        try:
            query = 'SELECT * FROM crawlContent WHERE expirationDate is NULL '
            cursor.execute(query)
            if cursor.rowcount == 0:
                response = False  # Not Exist
            else:
                response = []
                records = cursor.fetchall()
                for item in records:
                    out = {
                        'title': item[2],
                        'company': item[3],
                        'link': item[11],
                    }
                    response.append(out)
        except mysql.connector.Error as err:
            logging.error("Failed get Record: {}".format(err))
            response = 'Error'
        except Exception as err:
            logging.error("Failed get Record: {}".format(err))
            response = 'Error'
        finally:
            cursor.close()
            cnx.close()
            return response