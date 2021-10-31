from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class Order(Base):
    """ Order details """

    __tablename__ = "order_details"

    id = Column(Integer, primary_key=True)
    customer_id = Column(String(250), nullable=False)
    resturant_name = Column(String(250), nullable=False)
    delivery_loc = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    price = Column(Integer, nullable=False)
    
    def __init__(self, customer_id, resturant_name, delivery_loc, price):
        """ Initializes a order details """
        self.customer_id = customer_id
        self.resturant_name = resturant_name
        self.delivery_loc = delivery_loc
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.price = price
        

    def to_dict(self):
        """ Dictinary representation of a order details """
        dict = {}
        dict['id'] = self.id
        dict['customer_id'] = self.customer_id
        dict['resturant_name'] = self.resturant_name
        dict['delivery_loc'] = self.delivery_loc
        dict['price'] = self.price
        dict['date_created'] = self.date_created
        
        return dict