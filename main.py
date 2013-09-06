#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import cgi
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.api import rdbms
from apiclient.discovery import build
import json
from oauth2client.appengine import OAuth2Decorator
from apiclient.http import MediaFileUpload
import datetime

decorator = OAuth2Decorator(
    client_id = '1084112190775.apps.googleusercontent.com',
    client_secret = 'p24Uy-IqgZ_OyqzsqokOobBV',
    scope='https://www.googleapis.com/auth/calendar'
    )
service = build('calendar','v3')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

_INSTANCE_NAME = "prinya-th-2013:prinya-db"


class MainHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
    	# student_id = self.request.get('student_id');
    	student_id="2"
    	student_id=int(student_id)
    	conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
    	cursor = conn.cursor()
        sql="SELECT course_code,course_name,section_number,fol.regiscourse_id,fol.section_id FROM followcourse fol \
			join section sec \
			ON fol.section_id=sec.section_id \
			join course cou \
			ON course_id=sec.regiscourse_id \
			WHERE student_id='%d'"%(student_id)
    	cursor.execute(sql);

    	conn4 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor4 = conn4.cursor()
        sql4="SELECT course_code,course_name,s.section_number,credit_lecture,credit_lab,r.regiscourse_id,s.section_id,s.enroll \
        	FROM registeredcourse re join section s \
        	ON re.section_id=s.section_id join regiscourse r \
        	ON s.regiscourse_id=r.regiscourse_id join course c \
        	ON r.course_id=c.course_id \
        	WHERE student_id='%d'"%(student_id)
        cursor4.execute(sql4)
    
        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql="SELECT round(sum(credit_lecture+(credit_lab/3)),0)\
        	FROM registeredcourse re join section s\
        	ON re.section_id=s.section_id join regiscourse r \
        	ON s.regiscourse_id=r.regiscourse_id join course c \
        	ON r.course_id=c.course_id WHERE student_id='%d' GROUP BY student_id"%(student_id)
        cursor2.execute(sql)
        credit_enroll=""
        for row in cursor2.fetchall():
            credit_enroll=row[0]


        conn3 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor3 = conn3.cursor()
        sql2="SELECT maxcredit_per_semester \
        	FROM faculity f join student s \
        	ON f.faculity_id=s.faculity_id \
        	WHERE student_id='%d'"%(student_id)
        cursor3.execute(sql2)
        credit_total=""
        for row in cursor3.fetchall():
            credit_total=row[0]

        http = decorator.http()
        events = service.events().list(calendarId='primary').execute(http=http)
        year = []
        month = []
        date = []
        start_time_hour = []
        start_time_minute = []
        end_time_hour = []
        end_time_minute = []
        allday_time = []
        loca = ""
        location = []
        recurrence = []
        recurrence2 = []
        title = []


        for event in events['items']:
            if 'date' in event['start']:
                dateTime = event['start']['date']       
                if 'recurrence' in event:
                    rec = event['recurrence']
                    recurrence.append(rec)
                    year.append(dateTime[:4])
                    month.append(dateTime[5:-3])
                    date.append(dateTime[8:])      
                    start_time_hour.append(00)
                    start_time_minute.append(00)
                    end_time_hour.append(00)
                    end_time_minute.append(00)
                    allday_time.append(1) 
                    if 'location' in event:
                        loca = event['location']
                        location.append(loca)
                        if 'summary' in event:   
                            title.append(event['summary'])
                        else:
                            title.append(" ")
                    else:
                        location.append(" ")
                        if 'summary' in event:   
                            title.append(event['summary'])
                        else:
                            title.append(" ")
                else:
                    recurrence.append(0)
                    year.append(dateTime[:4])
                    month.append(dateTime[5:-3])
                    date.append(dateTime[8:])          
                    start_time_hour.append(00)
                    start_time_minute.append(00)
                    end_time_hour.append(00)
                    end_time_minute.append(00)
                    allday_time.append(1)       
                    if 'location' in event:
                        loca = event['location']
                        location.append(loca)
                        if 'summary' in event:   
                            title.append(event['summary'])
                        else:
                            title.append(" ")
                    else:
                        location.append(" ")
                        if 'summary' in event:   
                            title.append(event['summary'])
                        else:
                            title.append(" ")
            else:
                dateTime = event['start']['dateTime']
                dateTime2 = event['end']['dateTime']
                if 'recurrence' in event:
                    rec = event['recurrence']
                    recurrence.append(rec)
                    year.append(dateTime[:4])
                    month.append(dateTime[5:-18])
                    date.append(dateTime[8:-15])
                    start_time_hour.append(dateTime[11:-12])
                    start_time_minute.append(dateTime[14:-9])
                    end_time_hour.append(dateTime2[11:-12])
                    end_time_minute.append(dateTime2[14:-9])
                    allday_time.append(0)                                           
                    if 'location' in event:
                        loca = event['location']
                        location.append(loca)
                        if 'summary' in event:   
                            title.append(event['summary'])
                        else:
                            title.append(" ")
                    else:
                        location.append(" ")
                        if 'summary' in event:   
                            title.append(event['summary'])
                        else:
                            title.append(" ")
                else:
                    recurrence.append(0)
                    year.append(dateTime[:4])
                    month.append(dateTime[5:-18])
                    date.append(dateTime[8:-15])
                    start_time_hour.append(dateTime[11:-12])
                    start_time_minute.append(dateTime[14:-9])
                    end_time_hour.append(dateTime2[11:-12])
                    end_time_minute.append(dateTime2[14:-9])
                    allday_time.append(0)
                    if 'location' in event:
                        loca = event['location']
                        location.append(loca)
                        if 'summary' in event:   
                            title.append(event['summary'])
                        else:
                            title.append(" ")
                    else:
                        location.append(" ")
                        if 'summary' in event:   
                            title.append(event['summary'])
                        else:
                            title.append(" ")

        len_event = len(year)

        for row in range(0,len(recurrence)):
            if recurrence[row] != 0:
                rec = str(recurrence[row])
                x = list(str(recurrence[row]))
                if x[28] == "'" :
                    recurrence2.append(int(rec[27:-2]))
                else:           
                    recurrence2.append(int(rec[27:-2]))
            else:
                recurrence2.append(int(1))


        templates = {
            'events' : events['items'],
            'year' : year,
            'month' : month,
            'date' : date,  
            'start_time_hour' : start_time_hour,    
            'start_time_minute' : start_time_minute,    
            'end_time_hour' : end_time_hour,    
            'end_time_minute' : end_time_minute,    
            'allday_time' : allday_time,  
            'recurrence2' : recurrence2,    
            'len_event' : len_event,
            'location' : location,
    		'followcourse' : cursor.fetchall(),
    		'student_id' : student_id,
    		'regis' : cursor4.fetchall(),
            'credit_enroll' : credit_enroll,
            'credit_total' : credit_total,

    	}
    	get_template = JINJA_ENVIRONMENT.get_template('course_regis.html')
    	self.response.write(get_template.render(templates));

    	conn.close();
    	conn2.close();
    	conn3.close();
    	conn4.close();

class SearchCourseHandler(webapp2.RequestHandler):
    def get(self):
        
        student_id=self.request.get('student_id');
        student_id=int(student_id)

        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor = conn.cursor()
        sql="SELECT department_name from department"
        cursor.execute(sql);

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="SELECT title from faculity"
        cursor2.execute(sql2);

        templates = {
            'student_id' : student_id,
            'department' : cursor.fetchall(),
            'faculity' : cursor2.fetchall(),
            }

        template = JINJA_ENVIRONMENT.get_template('course_active.html')
        self.response.write(template.render(templates))

class SearchHandler(webapp2.RequestHandler):
    def get(self):
        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor = conn.cursor()
        sql="SELECT department_name from department"
        cursor.execute(sql);

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="SELECT title from faculity"
        cursor2.execute(sql2);

        student_id=self.request.get('student_id');
        student_id=int(student_id)
        course_code=self.request.get('keyword');
        year=self.request.get('year');
            
        semester=self.request.get('semester');
        check_code=0
        check_fac=0
        check_dep=0
        check_year=0
        check_sem=0
        allcheck=0
        key_year=""
        key_sem=""
        code=""

        if year=="":
            check_year=0
        else:
            check_year=1
            key_year="year="+year

        if semester=="":
            check_sem=0
        else:
            check_sem=1
            key_sem="semester="+semester

        if course_code == "":
            check_code=0

        else:
            check_code=1
            code="course_code like '%"+course_code+"%' "




        data_faculity=self.request.get('faculity');
        data_faculity=str(data_faculity)
        data_department_full=""
        

        if data_faculity =="":
            check_fac=0
        else:
            check_fac=1
            data_faculity_full="faculity='"+data_faculity+"'";



        data_department=self.request.get('department');
        data_department=str(data_department)
        data_department_full=""

        
        if data_department=="":
            check_dep=0
        else:
            check_dep=1
            data_department_full="department='"+data_department+"'"



        where_code=" "
        a=" and "



        if check_code == 1:
            if check_code == 1:
                where_code+=code
            if check_year == 1:
                where_code+=a
                where_code+=key_year
            if check_sem == 1:
                where_code+=a
                where_code+=key_sem
            if check_fac == 1:
                where_code+=a
                where_code+=data_faculity_full
            if check_dep==1:
                where_code+=a
                where_code+=data_department_full
        elif check_year == 1:
            if check_year == 1:
                where_code+=key_year
            if check_sem == 1:
                where_code+=a
                where_code+=key_sem
            if check_fac == 1:
                where_code+=a
                where_code+=data_faculity_full
            if check_dep==1:
                where_code+=a
                where_code+=data_department_full
        elif check_sem == 1:
            if check_sem == 1:
                where_code+=key_sem
            if check_fac == 1:
                where_code+=a
                where_code+=data_faculity_full
            if check_dep==1:
                where_code+=a
                where_code+=data_department_full
        elif check_fac == 1:
            if check_fac == 1:
                where_code+=data_faculity_full
            if check_dep==1:
                where_code+=a
                where_code+=data_department_full
        elif check_dep==1:
            if check_dep==1:
                where_code+=data_department_full
        else:
            where_code="course_id = 0"

            

        conn3 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor3 = conn3.cursor()
        sql3="SELECT course_id,course_code,course_name FROM course where %s "%(where_code)
        cursor3.execute(sql3)
        conn3.commit()


        # conn2=rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        # cursor2 = conn2.cursor()
        # cursor2.execute('SELECT sum(capacity),sum(enroll),regiscourse_id FROM section group by regiscourse_id')
        # conn2.commit()





        templates = {

        'course' : cursor3.fetchall(),
        'student_id' : student_id,
        'department' : cursor.fetchall(),
        'faculity' : cursor2.fetchall(),
        # 'enroll' : cursor2.fetchall(),


        }

        template = JINJA_ENVIRONMENT.get_template('course_active.html')
        self.response.write(template.render(templates))

        # conn.close()
        # conn2.close()

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class DetailCourseFollowHandler(webapp2.RequestHandler):
    def get(self):
        student_id = self.request.get('student_id');
        student_id=int(student_id)
    	course_code = self.request.get('course_code');
    	conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
    	cursor = conn.cursor()
        sql="SELECT * FROM course WHERE course_code='%s'"%(course_code)
    	cursor.execute(sql);

        credit=0
        conn4 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor4 = conn4.cursor()
        sql4="SELECT round(credit_lecture+(credit_lab/3),'0') FROM course WHERE course_code='%s'"%(course_code)
        cursor4.execute(sql4);
        for row in cursor4.fetchall():
            credit=row[0]
            if credit=="":
                credit=0

        conn5 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor5 = conn5.cursor()
        sql5="SELECT sum(capacity),sum(enroll) FROM section se JOIN regiscourse re\
            ON se.regiscourse_id=re.regiscourse_id\
            join course co\
            ON co.course_id=re.course_id\
            WHERE course_code='%s'"%(course_code)
        cursor5.execute(sql5);
        capacity=""
        enroll=""
        for row in cursor5.fetchall():
            capacity=row[0]
            enroll=row[1]

    	conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="SELECT co.course_code FROM course co,prerequsite_course pre\
            WHERE prerequsite_id=co.course_id AND pre.course_id=\
            (SELECT course_id FROM course WHERE course_code='%s')"%(course_code)
        cursor2.execute(sql2);
        pre_code=""
        for row in cursor2.fetchall():
            pre_code=row[0]

        conn3 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor3 = conn3.cursor()
        sql3="SELECT section_number,CASE day WHEN '1' THEN 'Sunday'\
            WHEN '2' THEN 'Monday'\
            WHEN '3' THEN 'Tuesday'\
            WHEN '4' THEN 'Wednesday'\
            WHEN '5' THEN 'Thursday'\
            WHEN '6' THEN 'Friday'\
            WHEN '7' THEN 'Saturday'\
            ELSE 'ERROR' END,\
            CONCAT(CONCAT(start_time,'-'),end_time),\
            UPPER(CONCAT(CONCAT(firstname,' '),lastname)),\
            enroll,capacity,sec.section_id,sec.regiscourse_id\
            FROM section sec JOIN section_time sct\
            ON sct.section_id=sec.section_id\
            JOIN course cou\
            ON sec.regiscourse_id=cou.course_id\
            JOIN staff sta\
            ON sta.staff_id=sec.teacher_id\
            WHERE course_code='%s'\
            ORDER BY section_number"%(course_code)
        cursor3.execute(sql3);

        conn6 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor6 = conn6.cursor()
        sql6="SELECT section_number\
            FROM followcourse fol JOIN course cou\
            ON fol.regiscourse_id=cou.course_id\
            JOIN section sec\
            ON sec.section_id=fol.section_id\
            WHERE student_id='%d' AND course_code='%s'"%(student_id,course_code)
        cursor6.execute(sql6);
        fol_sec=""
        for row in cursor6.fetchall():
            fol_sec=row[0]

        

    	templates = {
    		'course' : cursor.fetchall(),
    		'prerequsite_code' : pre_code,
    		'section' : cursor3.fetchall(),
            'capacity' : capacity,
            'credit' : credit,
            'enroll' : enroll,
            'fol_sec' : fol_sec,
            'student_id' : student_id,
    	}
    	get_template = JINJA_ENVIRONMENT.get_template('course_follow.html')
    	self.response.write(get_template.render(templates));
    	conn.close();
        conn2.close();
        conn3.close();
        conn4.close();
        conn5.close();
        conn6.close();

# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class CourseEnrollHandler(webapp2.RequestHandler):
    def get(self):
        student_id = self.request.get('student_id');
        student_id=int(student_id)
        course_code = self.request.get('course_code');
        capacity=""
		# course_id = "BIS-101"

        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor = conn.cursor()
        sql="SELECT * FROM course WHERE course_code = '%s'"%(course_code)
        cursor.execute(sql);

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="SELECT co.course_code FROM course co,prerequsite_course pre\
            WHERE prerequsite_id=co.course_id AND pre.course_id=\
            (SELECT course_id FROM course WHERE course_code='%s')"%(course_code)
        cursor2.execute(sql2);
        pre_code=""
        for row in cursor2.fetchall():
            pre_code=row[0]

        conn3 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor3 = conn3.cursor()
        sql3="SELECT sum(capacity),sum(enroll) FROM section se JOIN regiscourse re\
        	ON se.regiscourse_id=re.regiscourse_id\
        	join course co\
        	ON co.course_id=re.course_id\
        	WHERE course_code='%s'"%(course_code)
        cursor3.execute(sql3);
        enroll=""
        for capa in cursor3.fetchall():
        	if capa[0]!="":
        		capacity=capa[0]
        	else:
        		capacity=0
        	if capa[1]!="":
        		enroll=capa[1]
        	else:
        		enroll=0

        conn4 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor4 = conn4.cursor()
        sql4="SELECT section_number,CASE day WHEN '1' THEN 'Sunday'\
            WHEN '2' THEN 'Monday'\
            WHEN '3' THEN 'Tuesday'\
            WHEN '4' THEN 'Wednesday'\
            WHEN '5' THEN 'Thursday'\
            WHEN '6' THEN 'Friday'\
            WHEN '7' THEN 'Saturday'\
            ELSE 'NONE' END,CONCAT(CONCAT(start_time,'-'),end_time),\
            CASE teacher_id WHEN '1' THEN 'Tharnnapat'\
            WHEN '2' THEN 'Teerapol'\
            WHEN '3' THEN 'Vorachat'\
            ELSE 'NONE' END,CONCAT(CONCAT(enroll,'/'),capacity),enroll,capacity,sec.section_id,sec.regiscourse_id  \
        from section sec JOIN section_time sct on sec.section_id=sct.section_id \
        where regiscourse_id=(select regiscourse_id from regiscourse \
        	where course_id = (select course_id from course where course_code ='%s'))"%(course_code)
        cursor4.execute(sql4);



        credit=0
        conn5 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor5 = conn5.cursor()
        sql5="SELECT round(credit_lecture+(credit_lab/3),'0') FROM course WHERE course_code='%s'"%(course_code)
        cursor5.execute(sql5);
        for row2 in cursor5.fetchall():
            credit=row2[0]
        if credit=="":
            credit=0

        conn6 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor6 = conn6.cursor()
        sql6="SELECT re.section_id from registeredcourse re join section s on re.section_id=s.section_id join regiscourse r \
        		on s.regiscourse_id=r.regiscourse_id join course c on r.course_id=c.course_id \
        		where student_id=2 AND course_code='%s'"%(course_code)
        		# where student_id=2 AND course_code='%s'"%(course_code)
        cursor6.execute(sql6);
        check1=0
        for row3 in cursor6.fetchall():
        	check1=row3[0]
        	check1=int(check1)
        	if check1=="":
        		check1=0


        templates = {
        	'course' : cursor.fetchall(),
        	'capacity' : capacity,
            'prerequisite_code' : pre_code,
            'section' : cursor4.fetchall(),
            'credit' : credit,
            'enroll' : enroll,
            'credit' : credit,
            'course_code' : course_code,
            'check' : check1,
            'student_id' : student_id
        }
        get_template = JINJA_ENVIRONMENT.get_template('course_enroll2.html')
        self.response.write(get_template.render(templates));
        conn.close();
        conn2.close();
        conn3.close();
        conn4.close();
        conn5.close();
        conn6.close();

class EnrollHandler(webapp2.RequestHandler):
    def get(self):
        student_id = self.request.get('student_id');
        student_id=int(student_id)
    	course_code = self.request.get('course_code');
        section_number = self.request.get('section_number');
    	conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
    	cursor = conn.cursor()
        sql="SELECT round(sum(credit_lecture+(credit_lab/3)),'0')\
				from registeredcourse rec join course cou \
				ON cou.course_id=rec.regiscourse_id \
				join student stu \
				on stu.student_id=rec.student_id where rec.student_id='%d'"%(student_id)
    	cursor.execute(sql);
    	
    	credit=0
    	for row in cursor.fetchall():
    		credit=row[0]

    	conn4 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor4 = conn4.cursor()
        sql4="SELECT maxcredit_per_semester from faculity f join student s on f.faculity_id=s.faculity_id where student_id='%d'"%(student_id)
        cursor4.execute(sql4)
        credit_total=0
        for row2 in cursor4.fetchall():
            credit_total=row2[0]

        enroll = self.request.get('enroll');
    	enroll=int(enroll)
    	capacity = self.request.get('capacity');
    	capacity=int(capacity)
    	regiscourse_id = self.request.get('regiscourse_id');
    	regiscourse_id=int(regiscourse_id)
    	section_id = self.request.get('section_id');
    	section_id=int(section_id)

    	if credit>=credit_total:
    		self.redirect('/ErrorCredit')
    	elif enroll>=capacity:
    		self.redirect('/Error')
    	else :
            conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
            cursor2 = conn2.cursor()
            sql2="INSERT INTO registeredcourse(student_id,regiscourse_id,section_id) values('%d','%d','%d')"%(student_id,regiscourse_id,section_id)
            cursor2.execute(sql2);
            conn2.commit()

            enroll=enroll+1
            conn3 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
            cursor3 = conn3.cursor()
            sql3="UPDATE section SET enroll='%d' WHERE section_id='%d' and regiscourse_id='%d'"%(enroll,section_id,regiscourse_id)
            cursor3.execute(sql3);
            conn3.commit()

            conn4 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
            cursor4 = conn4.cursor()
            sql4="DELETE FROM followcourse WHERE student_id='%d' AND section_id='%d' AND regiscourse_id ='%d'"%(student_id,section_id,regiscourse_id)
            cursor4.execute(sql4);
            conn4.commit()


            conn2.close()
            conn3.close()
            conn4.close()

        conn5 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor5 = conn5.cursor()
        sql5="SELECT semester,course_code\
                from course cou join regiscourse rc \
                ON cou.course_id=rc.course_id \
                where cou.course_code = '%s'"%(course_code)
        cursor5.execute(sql5);
        conn5.commit() 

        semester = ""

        for row3 in cursor5.fetchall():
            semester=row3[0]  

        conn5.close()   		
    		
    	conn.close()

        self.redirect('/InsertCelendar?student_id='+str(student_id)+'&course_code='+str(course_code)+'&section='+str(section_number)+'&semester='+str(semester))

class ErrorHandler(webapp2.RequestHandler):
    def get(self):
    	templates = {
            # 'course' : cursor.fetchall(),
        }
        get_template = JINJA_ENVIRONMENT.get_template('Error.html')
        self.response.write(get_template.render(templates));



class ErrorCreditHandler(webapp2.RequestHandler):
    def get(self):
    	templates = {
            # 'course' : cursor.fetchall(),
        }
        get_template = JINJA_ENVIRONMENT.get_template('ErrorCredit.html')
        self.response.write(get_template.render(templates));	

class UnenrollHandler(webapp2.RequestHandler):
    def get(self):

    	student_id=self.request.get('student_id')
        student_id=int(student_id)
        regiscourse_id=self.request.get('regiscourse_id')
    	regiscourse_id=int(regiscourse_id)
    	section_id=self.request.get('section_id')
    	section_id=int(section_id)
    	enroll=self.request.get('enroll')
    	enroll=int(enroll)
    	enroll=enroll-1


        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor = conn.cursor()
        sql="DELETE from registeredcourse where student_id='%d' and regiscourse_id='%d'"%(student_id,regiscourse_id)
        cursor.execute(sql)
        conn.commit();

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="UPDATE section set enroll='%d' where section_id='%d'"%(enroll,section_id)
        cursor2.execute(sql2)
        conn2.commit();
        conn.close();
        conn2.close();
        self.redirect('/DeleteCalendar?student_id='+str(student_id)+'&regiscourse_id='+str(regiscourse_id)+'&course_code='+str(course_code)+'&section_id='+str(section_id))

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class removeregistered(webapp2.RequestHandler):
    def get(self):

        student_id=self.request.get('student_id')
        student_id=int(student_id)
        regiscourse_id=self.request.get('regiscourse_id')
        regiscourse_id=int(regiscourse_id)
        section_id=self.request.get('section_id')
        section_id=int(section_id)
        course_code=self.request.get('course_code');
        enroll=self.request.get('enroll')
        enroll=int(enroll)
        enroll=enroll-1


        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor = conn.cursor()
        sql="DELETE from registeredcourse where student_id='%d' and regiscourse_id='%d'"%(student_id,regiscourse_id)
        cursor.execute(sql)
        conn.commit();

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="UPDATE section set enroll='%d' where section_id='%d'"%(enroll,section_id)
        cursor2.execute(sql2)
        conn2.commit();


        conn.close();
        conn2.close();



        self.redirect('/DeleteCalendar?student_id='+str(student_id)+'&regiscourse_id='+str(regiscourse_id)+'&course_code='+str(course_code)+'&section_id='+str(section_id))

class DetailCourse(webapp2.RequestHandler):
    def get(self):
        student_id=self.request.get('student_id')
        student_id=int(student_id)
    	course_id = self.request.get('course_code');

    	conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
    	cursor = conn.cursor()
        sql="SELECT * FROM course WHERE course_code = '%s'"%(course_id)
    	cursor.execute(sql);

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="SELECT co.course_code FROM course co,prerequsite_course pre\
            WHERE prerequsite_id=co.course_id AND pre.course_id=\
            (SELECT course_id FROM course WHERE course_code='%s')"%(course_id)
        cursor2.execute(sql2);
        pre_code=""
        for row in cursor2.fetchall():
            pre_code=row[0]

        conn3 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor3 = conn3.cursor()
        sql3="SELECT section_number,CASE day WHEN '1' THEN 'Sunday'\
            WHEN '2' THEN 'Monday'\
            WHEN '3' THEN 'Tuesday'\
            WHEN '4' THEN 'Wednesday'\
            WHEN '5' THEN 'Thursday'\
            WHEN '6' THEN 'Friday'\
            WHEN '7' THEN 'Saturday'\
            ELSE 'ERROR' END,\
            CONCAT(CONCAT(start_time,'-'),end_time),\
            UPPER(CONCAT(CONCAT(firstname,' '),lastname)),\
            CONCAT(CONCAT(enroll,'/'),capacity),sec.regiscourse_id,sec.section_id,enroll,capacity\
            FROM section sec JOIN section_time sct\
            ON sct.section_id=sec.section_id\
            JOIN course cou\
            ON sec.regiscourse_id=cou.course_id\
            JOIN staff sta\
            ON sta.staff_id=sec.teacher_id\
            WHERE course_code='%s'"%(course_id)
        cursor3.execute(sql3);

        conn4 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor4 = conn4.cursor()
        sql4="SELECT sum(capacity),sum(enroll) FROM section se JOIN regiscourse re\
            ON se.regiscourse_id=re.regiscourse_id\
            join course co\
            ON co.course_id=re.course_id\
            WHERE course_code='%s'"%(course_id)
        cursor4.execute(sql4);
        capacity=""
        enroll=""
        for row in cursor4.fetchall():
            capacity=row[0]
            enroll=row[1]

        conn5 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor5 = conn5.cursor()
        sql5="SELECT re.section_id from registeredcourse re join section s \
            on re.section_id=s.section_id join regiscourse r \
            on s.regiscourse_id=r.regiscourse_id join course c \
            on r.course_id=c.course_id \
            where student_id='%d' AND course_code='%s'"%(student_id,course_id)
        cursor5.execute(sql5);
        # sectionregistered=""
        # for row2 in cursor5.fetchall():
        #     sectionregistered=row2[0]




        templates = {
    		'course' : cursor.fetchall(),
            'prerequisite_code' : pre_code,
            'section' :cursor3.fetchall(),
            'capacity' :capacity,
            'enroll' :enroll,
            'sectionregistered' :cursor5.fetchall(),
            'student_id' : student_id
    	}
    	get_template = JINJA_ENVIRONMENT.get_template('course_enroll1.html')
    	self.response.write(get_template.render(templates));
        conn.close();
        conn2.close();
        conn3.close();

class ChangeCourse(webapp2.RequestHandler):
    def get(self):

        student_id=self.request.get('student_id')
        student_id=int(student_id)
        enroll = self.request.get('enroll');
        section_id = self.request.get('section_id');
        regiscourse_id = self.request.get('regiscourse_id');
        sec_id = self.request.get('sec_id');
        section_id=int(section_id)
        regiscourse_id=int(regiscourse_id)
        sec_id=int(sec_id)

        enroll=int(enroll)
        enroll=enroll+1

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="UPDATE registeredcourse set section_id ='%d' WHERE student_id = '%d' and regiscourse_id='%d'"%(section_id,student_id,regiscourse_id)
        cursor2.execute(sql2);
        conn2.commit()

        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor = conn.cursor()
        sql="UPDATE section set enroll='%d' WHERE section_id = '%d' "%(enroll,section_id)
        cursor.execute(sql);
        conn.commit()

        conn3 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor3 = conn3.cursor()
        sql3="SELECT enroll from section where section_id ='%d'"%(sec_id)
        cursor3.execute(sql3);
        conn3.commit()
        roll=""
        for row in cursor3.fetchall():
            roll=row[0]
        roll=int(roll)
        roll=roll-1
        self.response.write(roll)

        conn4 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor4 = conn4.cursor()
        sql4="UPDATE section set enroll='%d' WHERE section_id = '%d'"%(roll,sec_id)
        cursor4.execute(sql4);
        conn4.commit()

        conn.close()
        conn2.close()
        conn3.close()
        conn4.close()
        self.redirect('/SendMail?student_id='+str(student_id)+'&regiscourse_id='+str(regiscourse_id))


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class FollowHandler(webapp2.RequestHandler):
	def get(self):
            student_id = self.request.get('student_id');
            student_id=int(student_id)
            regiscourse_id = self.request.get('regiscourse_id');
            regiscourse_id=int(regiscourse_id)
            section_id = self.request.get('section_id');
            section_id=int(section_id)

            conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
            cursor = conn.cursor()
            sql="DELETE FROM followcourse WHERE student_id='%d' AND regiscourse_id='%d'"%(student_id,regiscourse_id)
            cursor.execute(sql);
            conn.commit();
            conn.close();

            conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
            cursor2 = conn2.cursor()
            sql2="INSERT INTO followcourse (student_id,regiscourse_id,section_id) VALUES ('%d','%d','%d')"%(student_id,regiscourse_id,section_id)
            cursor2.execute(sql2);
            conn2.commit();
            conn2.close();
            self.redirect('/?student_id='+str(student_id))

class UnFollowHandler(webapp2.RequestHandler):
	def get(self):
		student_id = self.request.get('student_id');
		student_id=int(student_id)
		regiscourse_id = self.request.get('regiscourse_id');
		regiscourse_id=int(regiscourse_id)
		section_id = self.request.get('section_id');
		section_id=int(section_id)

		conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
		cursor = conn.cursor()
		sql="DELETE FROM followcourse WHERE student_id='%d' AND regiscourse_id='%d' AND section_id='%d'"%(student_id,regiscourse_id,section_id)
		cursor.execute(sql);
		conn.commit();
		conn.close();

		self.redirect('/?student_id='+str(student_id))

# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class BillingHandler(webapp2.RequestHandler):
	def get(self):
		# student_id = self.request.get('student_id');
		student_id="2"
		student_id=int(student_id)
		price=0

		conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
		cursor = conn.cursor()
		sql="SELECT course_code,credit_lecture+(credit_lab/3) AS credit,price \
    		FROM registeredcourse reg JOIN course cou \
    		ON reg.regiscourse_id=cou.course_id WHERE student_id='%d'"%(student_id)
		cursor.execute(sql);
		# cursor.fetchall():

		conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
		cursor2 = conn2.cursor()
		sql2="SELECT SUM(price) FROM registeredcourse reg JOIN course cou \
    		ON reg.regiscourse_id=cou.course_id WHERE student_id='%d'"%(student_id)
		cursor2.execute(sql);
		for row in cursor2.fetchall():
			price=row[0]

		conn.commit();
		conn.close();
		conn2.commit();
		conn2.close();
		self.redirect('/?student_id='+str(student_id))

class SendMailHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user is None:
            login_url = users.create_login_url(self.request.path)
            self.redirect(login_url)
            return
        else:
            student_id=self.request.get('student_id');
            student_id=int(student_id)
            regiscourse_id=self.request.get('regiscourse_id');
            regiscourse_id=int(regiscourse_id)
            email=""
            course_code=""
            conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
            cursor = conn.cursor()
            sql="SELECT email,course_code FROM followcourse fwc JOIN student stu\
                ON fwc.student_id=stu.student_id\
                JOIN course cou\
                ON fwc.regiscourse_id=cou.course_id WHERE regiscourse_id='%d'\
                ORDER BY follow_id"%(regiscourse_id)
            cursor.execute(sql);
            for row in cursor.fetchall():
                email=row[0]
                course_code=row[1]
                break
            if email!="":
                user=users.get_current_user()
                message=mail.EmailMessage()
                message.sender=user.email()
                message.to=email
                message.subject="Subject "+course_code+" is avaliable NOW!!"
                message.body="You can enroll this course nowwww"
                message.send()
            self.redirect('/?student_id='+str(student_id))

class InsertCelendar(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):


        course_code = self.request.get('course_code');
        section = self.request.get('section');
        section_id= int(section)
        student_id = self.request.get('student_id');

        today = datetime.datetime.now()
        weekday = today.weekday()+2
        if weekday == 6 :
            weekday = 1 

        semester = self.request.get('semester');

        start_semester = ""
        end_semester = ""    

        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')

        cursor3 = conn.cursor()
        sql ="select * from semester where semester_id = '%s'"%(semester)
        cursor3.execute(sql)
        conn.commit() 
        for x in cursor3.fetchall():
            start_semester = str(x[1])
            end_semester = str(x[2])

        open_semester_year = start_semester

        num = 0

        new_start_date = datetime.datetime.strptime(start_semester, "%Y-%m-%d").date()
        new_end_date = datetime.datetime.strptime(end_semester, "%Y-%m-%d").date()


        new_start_date2 = str(new_start_date)  
        cut_year = int(new_start_date2[:4])
        month_num=int(new_start_date2[5:-3])
        day_num =int(new_start_date2[8:])

        while (new_start_date <= new_end_date ) :
            new_start_date = new_start_date + datetime.timedelta(days=+7)
            num += 1
            
        weekly_study = num



        
        cursor = conn.cursor()
        sql ="select day,start_time,end_time,room from\
                section sec JOIN section_time sct\
                ON sec.section_id=sct.section_id\
                JOIN course cou\
                ON cou.course_id=sec.regiscourse_id\
                WHERE course_code='%s' AND section_number='%s'"%(course_code,section)

        cursor.execute(sql)
        conn.commit()
        result = cursor.fetchall()


        cursor2 = conn.cursor()
        sql ="select room from\
                section sec JOIN section_time sct\
                ON sec.section_id=sct.section_id\
                JOIN course cou\
                ON cou.course_id=sec.regiscourse_id\
                WHERE course_code='%s' AND section_number=(select section_number from section_time where section_id='%s')"%(course_code,section_id)

        cursor2.execute(sql)
        conn.commit() 
        room = ""
        for x in cursor2.fetchall():
            room.append(x)



        day = []
        full_start_time =[]
        full_end_time = []
        room = []

        insert_day = []
        insert_day2 = []
        month_num2=[]


        for x in range(0,len(result)):
            day.append(result[x][0])
            full_start_time.append(result[x][1])        
            full_end_time.append(result[x][2])
            room.append(result[x][3])


        for x in range(0,len(result)):
            for d in range(1,8):  
                if d==result[x][0]:
                    if month_num==1 or month_num==3 or month_num==5 or month_num==7 or month_num==8 or month_num==10 or month_num==12 :
                        if day_num+d <= 31 :                    
                            insert_day.append(day_num+d-2)
                            month_num2.append(month_num)
                        else:
                            insert_day.append(day_num+d-33)
                            month_num2.append(month_num+1)                                              
                                        
                    elif month_num==4 or month_num==6 or month_num==9 or month_num==11:
                        if day_num+d <= 30 :                    
                            insert_day.append(day_num+d-2)
                            month_num2.append(month_num)
                        else:
                            insert_day.append(day_num+d-32)
                            month_num2.append(month_num+1)
                                                
                    elif month_num==2:
                        if day_num+d <= 28 :                    
                            insert_day.append(day_num+d-2)
                            month_num2.append(month_num)
                        else:
                            insert_day.append(day_num+d-30)
                            month_num2.append(month_num+1)                                                  
        
        for x in range(0,len(insert_day)):
            insert_day2.append(str(cut_year)+'-'+str(month_num2[x])+'-'+str(insert_day[x]))   


        self.response.write(insert_day2)
        
        http = decorator.http()
        for num in range(0,len(day)):
            event = {
                'summary' : "%s"%(course_code),
                'location' : room[num],
                'start' : {
                    'dateTime' : "%sT%s.000+07:00"%(insert_day2[num],full_start_time[num]),
                    'timeZone' : 'Asia/Bangkok'
                },
                'end':{
                    'dateTime' : "%sT%s.000+07:00"%(insert_day2[num],full_end_time[num]),
                    'timeZone' : 'Asia/Bangkok'
                },
                'recurrence': [
                "RRULE:FREQ=WEEKLY;COUNT=%d"%(weekly_study),
                ],       
            }

            insert_event = service.events().insert(calendarId='primary',body=event).execute(http=http)


        self.redirect('/?student_id='+str(student_id))


class DeleteCalendar(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):

        course_code = self.request.get('course_code');
        section_id = self.request.get('section_id');
        # section_id = int(section_id)
        student_id = self.request.get('student_id');
        regiscourse_id = self.request.get('regiscourse_id');

        http = decorator.http()
        events = service.events().list(calendarId='primary').execute(http=http)
        ID_events = []
        name_events = []

        for event in events['items']:
            if 'summary' in event:
                id_event = event['id']
                name_event = event['summary']
                ID_events.append(id_event)
                name_events.append(name_event)

        for y in range(0,len(ID_events)):   
            if course_code == name_events[y]:
                http = decorator.http()
                service.events().delete(calendarId='primary', eventId=ID_events[y]).execute(http=http)

        self.redirect('/SendMail?student_id='+str(student_id)+'&regiscourse_id='+str(regiscourse_id))


        
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/SearchCourse', SearchCourseHandler), 
    ('/FollowingDetailCourse', DetailCourseFollowHandler),
    ('/Follow', FollowHandler),
    ('/UnFollow', UnFollowHandler),
    ('/Billing', BillingHandler),
    ('/SendMail', SendMailHandler),
    ('/Search', SearchHandler),
    ('/CourseEnroll', CourseEnrollHandler),
    ('/Enroll', EnrollHandler),
    ('/Error', ErrorHandler),
    ('/ErrorCredit', ErrorCreditHandler),
    ('/Unenroll', UnenrollHandler),
    ('/removeregistered',removeregistered),
    ('/detailCourse',DetailCourse),
    ('/Change',ChangeCourse),
    ('/InsertCelendar', InsertCelendar),
    ('/DeleteCalendar', DeleteCalendar),
    (decorator.callback_path,decorator.callback_handler()),
], debug=True)
