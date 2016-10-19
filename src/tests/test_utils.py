from main import *


def test_ID():
   value = '1000'
   i_valid = 1000
   s_valid = '000001000'
   _id = ID(value)
   assert _id.int == i_valid
   assert _id.str == s_valid

   value = '011-000'
   i_valid = 11000
   s_valid = '000011000'
   _id = ID(value)
   assert _id.int == i_valid
   assert _id.str == s_valid

   value = '121-1000'
   i_valid = 1211000
   s_valid = '001211000'
   _id = ID(value)
   assert _id.int == i_valid
   assert _id.str == s_valid

   value = 'asd1000'
   _id = ID(value)
   assert _id.int == None
   assert _id.str == None
