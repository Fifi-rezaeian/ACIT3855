from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class ScheduledOrder(Base):
    """ Scheduled Order """

    __tablename__ = "scheduled_order"

    id = Column(Integer, primary_key=True)
    customer_id = Column(String(250), nullable=False)
    resturant_name = Column(String(250), nullable=False)
    delivery_loc = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    scheduled_time = Column(Integer, nullable=False)
    
    def __init__(self, customer_id, resturant_name, delivery_loc, scheduled_time):
        """ Initializes a  scheduled order details """
        self.customer_id = customer_id
        self.resturant_name = resturant_name
        self.delivery_loc = delivery_loc
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.scheduled_time = scheduled_time
        

    def to_dict(self):
        """ Dictinary representation of a  scheduled order details """
        dict = {}
        dict['id'] = self.id
        dict['customer_id'] = self.customer_id
        dict['resturant_name'] = self.resturant_name
        dict['delivery_loc'] = self.delivery_loc
        dict['scheduled_time'] = self.scheduled_time
        dict['date_created'] = self.date_created
        
        return dict