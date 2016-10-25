from main import *


def test_ID():
   value = '1000'
   i_valid = 1000
   s_valid = '000001000'
   _id = ID(value)
   assert _id.int == i_valid
   assert _id.str == s_valid

   value = '011 000'
   i_valid = 11000
   s_valid = '000011000'
   _id = ID(value)
   assert _id.int == i_valid
   assert _id.str == s_valid

   value = '121 1000'
   i_valid = 1211000
   s_valid = '001211000'
   _id = ID(value)
   assert _id.int == i_valid
   assert _id.str == s_valid

   value = 'asd1000'
   _id = ID(value)
   assert _id.int == None
   assert _id.str == None


def test_ExpiresDate():
    cur_date = DT.datetime.utcnow()
    cur1_date = cur_date - DT.timedelta(seconds=200)
    ex_dt_obj = cur_date - DT.timedelta(seconds=100)
    ex_date = ExpiresDate(ex_dt_obj)
    
    # Check ExpiresDate check
    assert ex_date.check_now() == False
    assert ex_date.check_date(cur1_date) == True
    
    # Check ExpiresDate propertyes
    assert ex_date.timestamp == ex_dt_obj.timestamp()
    assert ex_date.dt == ex_dt_obj
    assert ex_date.dt == ex_dt_obj
    assert ExpiresDate.from_now().check_date(cur1_date) == True
    
    # Check create ExpiresDate from timestamp
    assert ExpiresDate(ex_dt_obj.timestamp()).dt == ex_dt_obj
    assert ExpiresDate(str(ex_dt_obj.timestamp())).dt == ex_dt_obj

    # Check create with delta
    ex1_dt_obj = cur_date + DT.timedelta(seconds=600)
    assert ExpiresDate(cur_date, 600).dt == ex1_dt_obj

