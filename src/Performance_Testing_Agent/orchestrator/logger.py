import logging

#configure logging 
logging.basicConfig(
 
    level=logging.INFO,
 
    format="%(asctime)s - %(levelname)s - %(message)s"
 
)

#create logger 
logger = logging.getLogger("Performance Testing Agent")