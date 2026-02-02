import random

class RussianRouletteGame:
    def __init__(self):
        self.chambers = [0, 0, 0, 0, 0, 1]
        random.shuffle(self.chambers)
        self.current_index = 0
        self.is_alive = True
        self.score = 0
    
    def shoot(self):
        if not self.is_alive:
            return "you lose!!!"
        
        result = self.chambers[self.current_index]
        self.current_index += 1

        if result == 1:
            self.is_alive = False
            return "boom"
        else:
            self.score += 1
            return 'click'
    
    def stop(self):
        self.is_alive = False
        return self.score
    