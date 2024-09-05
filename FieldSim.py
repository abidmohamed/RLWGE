import random

from DateSim import DateSIM

class FieldSim:

  def __init__(self,  day, month, num_days, mode='static'):
    self.num_days= num_days
    self.simulation = DateSIM(day, month, num_days, 0)
    
    if mode == 'static':
      self.InitStatic()
    elif mode == 'random':
      self.InitRandom()

  def InitStatic(self):
    self.water_quantity = 0
    self.crop_health = 50

  def InitRandom(self):
    self.water_quantity = round(random.uniform(0,5), 2)
    self.crop_health = random.randint(10, 100)


  def validateMove(self):
    outcome = 0 # valid Move 1 invalide move 2 game lost 3 game won 
    if self.crop_health <= 0:
      outcome = 2
    if self.simulation.num_days <= 0 and self.crop_health > 45:
      outcome = 3
    
    if self.simulation.num_days <= 0:
      outcome = 1
    
    return outcome

  def makeMove(self, action):

    def checkMove(quantity):
      
      if self.validateMove() == 0:
        if quantity == -2:
          self.water_quantity = 0
          self.num_days -= 1
          self.simulation.run_date()
        else:
          new_quantity = self.water_quantity + quantity
          self.water_quantity = new_quantity
          self.num_days -= 1
          self.simulation.run_date()
        
    if action == 'u': #up
      checkMove(1)
    if action == 'd': #down
      checkMove(-1)
    if action == 'h': #hold
      checkMove(0)
    if action == 's': #stop
      checkMove(-2)

  def reward(self):
    crop_status = self.simulation.crop_sim.crop_state(self.simulation.daily_irrigation, self.water_quantity)
    # print("Crop Status ", crop_status)
    if ( crop_status > 0):
      self.crop_health -= crop_status
      self.crop_health = round(self.crop_health, 2)
      if self.crop_health <= 0:
        return -10
      else:
        return -1
    
    elif ( crop_status < 0):
      self.crop_health -= (-crop_status)
      self.crop_health = round(self.crop_health, 2)
      if self.crop_health <= 0:
        return -10
      else:
        return -1

    elif self.simulation.num_days <= 0 and self.crop_health > 45:
      return 1
    elif self.simulation.num_days <= 0 and self.crop_health < 45:
        return -10


  def display(self):
    return self.crop_health, self.water_quantity, self.num_days

def main():
    foo = FieldSim(1, 1, 2)
    foo.makeMove('u')
    foo.makeMove('u')
    
    print(foo.reward())
    print(foo.display())

if __name__ == "__main__":
    main()
