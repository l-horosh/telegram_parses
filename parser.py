from helpers import DBOption



class Post():
      brand = None
      model = None
      region = None
      price = None
      attributes_list = None

      def __init__(self, message: str):
            dash_split = [s.strip() for s in message.split('➖') if s.strip() != '']
            
            brand_model_list = dash_split[1].split()
            self.brand = brand_model_list[0]
            
            self.model = " ".join(brand_model_list[1:])
            
            region_split_list = [s.strip() for s in dash_split[2].split('🟢') if s.strip() != '']
            self.region = " ".join(region_split_list[0].split()[1:])[1:]
            
            price_split = [s.strip() for s in dash_split[3].split('\n') if s.strip() != '']
            self.price = int(price_split[1].replace(" ", "")[:-1])

            self.fill_attributes()

      def fill_attributes(self):
            self.attributes_list = []
            self.attributes_list.append((self.brand, DBOption.BRAND))
            self.attributes_list.append((self.model, DBOption.MODEL))
            self.attributes_list.append((self.region, DBOption.LOCATION))




