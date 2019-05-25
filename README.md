# Bid Calculation

### Dependencies
  - Python 2.7.x
  - Postgres SQL
  - Psycopg2 

### Set up
  - Unzip the submitted file into current directory
  - Run setDb.sql on postgres terminal
  - Run fill_tables.py with the folder path to the input files as argument (folder path should have no spaces), postgres username and password.
  `python fill_tables.py <folder_path> <username> <password>`
  Eg: `python fill_tables.py /home/krithika postgres 5656`
 

### To generate bidupload.csv
  - Run bid_calc.py with postgres username and password as argument
  `python bid_calc.py <username> <password>`
   Eg: `python bid_calc.py postgres 5656`
 
### Assumptions
  - ASR in make_model_asr is the value for ARS (Average Revenue per Sale)
  - All the numbers in csv files are in number format ( no commas, no '$' sign)
  - All the keywords strings in csv files are properly formatted ( words and numbers separated by space, no '+' character)
  - There is no other database already named 'carvana' on localhost
  * For the specified keyword, the following attributes are sum of all those attribute for that keyword
      * Est First pos Bid
      * Est Top page bid
      * AG conversions
      * AG CVR
      * Mk/Mo/Yr conversions
      * Mk/Mo/Yr CVR
      * Mk/Mo conversions
      * Mk/Mo CVR
      * Mkt conversion, Mkt CVR
  - current onsite inventory and hist inventory are the sum of all the values for the specified make, model, year. (The input file has replicated each row 8 times. I have considered them valid)
  * Adjusting Bid based on Mkt CVR is done as follows:
       * difference percentage = (overall CVR - CVR for mkt of the specified keyword) / 2  * 100
       * new bid price = (old bid price * difference percentage ) / 100
  - QS is the avreage of all the quality score for the specified keyword
  - in bid [], the second argument 0 = bid calculated based on KW or AG, 1 = bid calculated based on Mk/Mo/Yr or Mk/Mo
  - For KWs with QS<8 and QS>5 cannot be higher than average of Est Top of Page Bid and Est First Pos Bid, I have capped the bid at max(Est Top of Page Bid, Est First Pos Bid) 
