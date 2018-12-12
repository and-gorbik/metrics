import unittest
import json

# позволяет подменять функции класса другими функциями
from unittest.mock import patch

from example import Asteroid

class TestAsteroid(unittest.TestCase):
    # этот метод устанавливает начальные данные для каждого
    # unittest'a (метода, начинающегося с "test_")
    def setUp(self):
        self.asteroid = Asteroid(2099942)
    
    # этот метод очищает/закрывает/удаляет ресурсы в конце
    # каждого unittest'a.
    def tearDown(self):
        pass

    def mocked_get_data(self):
        with open('apophis_fixture.txt') as f:
            return json.loads(f.read())

    @patch('example.Asteroid.get_data', mocked_get_data)
    def test_name(self):
        self.assertEqual(
            self.asteroid.name, '99942 Apophis (2004 MN4)'
        )
    
    @patch('example.Asteroid.get_data', mocked_get_data)
    def test_diameter(self):
        self.assertEqual(self.asteroid.diameter, 682)
    

