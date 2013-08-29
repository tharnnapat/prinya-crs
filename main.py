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
from google.appengine.api import rdbms
import datetime

decorator = OAuth2Decorator(
    client_id = '1084112190775.apps.googleusercontent.com',
    client_secret = 'p24Uy-IqgZ_OyqzsqokOobB',
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

        for event in events['items']:
            if 'dateTime' in event['start']:
                dateTime = event['start']['dateTime']
                dateTime2 = event['end']['dateTime']
                year.append(dateTime[:4])
                month.append(dateTime[5:-18])
                date.append(dateTime[8:-15])
                start_time_hour.append(dateTime[11:-12])
                start_time_minute.append(dateTime[14:-9])
                end_time_hour.append(dateTime2[11:-12])
                end_time_minute.append(dateTime2[14:-9])
                allday_time.append(0)
                                                                                                                            
            else:
                dateTime = event['start']['date']
                dateTime2 = event['end']['date']
                year.append(dateTime[:4])
                month.append(dateTime[5:-3])
                date.append(dateTime[8:])      
                start_time_hour.append(00)
                start_time_minute.append(00)
                end_time_hour.append(00)
                end_time_minute.append(00)
                allday_time.append(1)


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
        templates = {
            'student_id' : student_id
            }

        template = JINJA_ENVIRONMENT.get_template('course_active.html')
        self.response.write(template.render(templates))

class SearchHandler(webapp2.RequestHandler):
    def get(self):
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




        data_faculity_id=self.request.get('faculity');
        data_faculity_id=str(data_faculity_id)
        data_faculity=""

        if data_faculity_id=="1":
            data_faculity = "faculity='Engineering'";
        elif data_faculity_id=="2":
            data_faculity = "faculity='Information Technology'";
        elif data_faculity_id=="3":
            data_faculity = "faculity='Business Administration'";
        elif data_faculity_id=="4":
            data_faculity = "faculity='Language'";

        if data_faculity_id =="":
            check_fac=0
        else:
            check_fac=1



        data_department=self.request.get('department');
        data_department=str(data_department)
        data_department_full=""

        if data_department=="1":
            data_department_full="department='Information Technology'"
        elif data_department=="2":
            data_department_full="department='Multimedia Technology'"
        elif data_department=="3":
            data_department_full="department='Business Information Technology'"
        elif data_department=="4":
            data_department_full="department='Accountancy'"
        elif data_department=="5":
            data_department_full="department='Industrial Management'"
        elif data_department=="6":
            data_department_full="department='International Business Management'"
        elif data_department=="7":
            data_department_full="department='Japanese Businees Administration'"
        elif data_department=="8":
            data_department_full="department='Computer Engineering'"
        elif data_department=="9":
            data_department_full="department='Production Engineering'"
        elif data_department=="10":
            data_department_full="department='Automotive Engineering'"
        elif data_department=="11":
            data_department_full="department='Electrical Engineering'"
        elif data_department=="12":
            data_department_full="department='Industrial Engineering'"
        elif data_department=="13":
            data_department_full="department='Language'"

        if data_department=="":
            check_dep=0
        else:
            check_dep=1



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
                where_code+=data_faculity
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
                where_code+=data_faculity
            if check_dep==1:
                where_code+=a
                where_code+=data_department_full
        elif check_sem == 1:
            if check_sem == 1:
                where_code+=key_sem
            if check_fac == 1:
                where_code+=a
                where_code+=data_faculity
            if check_dep==1:
                where_code+=a
                where_code+=data_department_full
        elif check_fac == 1:
            if check_fac == 1:
                where_code+=data_faculity
            if check_dep==1:
                where_code+=a
                where_code+=data_department_full
        elif check_dep==1:
            if check_dep==1:
                where_code+=data_department_full
        else:
            where_code="course_id = 0"

            

        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor = conn.cursor()
        sql="SELECT course_id,course_code,course_name FROM course where %s "%(where_code)
        cursor.execute(sql)
        conn.commit()


        # conn2=rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        # cursor2 = conn2.cursor()
        # cursor2.execute('SELECT sum(capacity),sum(enroll),regiscourse_id FROM section group by regiscourse_id')
        # conn2.commit()





        templates = {

        'course' : cursor.fetchall(),
        'student_id' : student_id,
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
    	# course_code = self.request.get('course_code');
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
    		
    		

    	conn.close()
    	self.redirect('/?student_id='+str(student_id))

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
        self.redirect('/SendMail?student_id='+str(student_id)+'&regiscourse_id='+str(regiscourse_id))

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class removeregistered(webapp2.RequestHandler):
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

        self.redirect('/SendMail?student_id='+str(student_id)+'&regiscourse_id='+str(regiscourse_id))

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
    (decorator.callback_path,decorator.callback_handler()),
], debug=True)
