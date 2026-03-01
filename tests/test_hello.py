import unittest
import sys
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from astro_engine import (
    get_rasi, get_nak, get_pada, fmt_deg, fmt_date, 
    get_rasi_name, get_nak_name, get_planet_name,
    LUCKY_NUMS, LUCKY_COLORS, RASIS, NAKS
)


class TestAstroEngine(unittest.TestCase):
    """Test suite for astro_engine functions"""
    
    def test_get_rasi(self):
        """Test rasi calculation from longitude"""
        # Rasi 0 corresponds to Aries (0-30 degrees)
        # Rasi 1 corresponds to Taurus (30-60 degrees)
        result = get_rasi(15)  # Should return 0 (Aries)
        self.assertEqual(result, 0)
        
        result = get_rasi(45)  # Should return 1 (Taurus)
        self.assertEqual(result, 1)
    
    def test_get_nak(self):
        """Test nakshatra calculation from longitude"""
        # Test that function returns a valid nakshatra index (0-26)
        result = get_nak(0)
        self.assertIsInstance(result, int)
        self.assertTrue(0 <= result < 27)
    
    def test_get_pada(self):
        """Test pada calculation from longitude"""
        # Test that pada is between 0-3
        result = get_pada(0)
        self.assertIsInstance(result, int)
        self.assertTrue(0 <= result < 4)
    
    def test_fmt_deg(self):
        """Test degree formatting"""
        result = fmt_deg(12.5)
        self.assertIsInstance(result, str)
        self.assertIn('°', result)  # Should contain degree symbol
    
    def test_fmt_date(self):
        """Test date formatting"""
        from datetime import date
        result = fmt_date(date(1990, 5, 15))
        self.assertIsInstance(result, str)
        self.assertIn('/', result)  # Should contain date separators
    
    def test_get_rasi_name(self):
        """Test rasi name retrieval"""
        # Get English name for Aries (index 0)
        result = get_rasi_name(0, 'en')
        self.assertEqual(result, 'Mesha')
        
        # Get Tamil name for Aries
        result = get_rasi_name(0, 'ta')
        self.assertEqual(result, 'மேஷம்')
    
    def test_get_nak_name(self):
        """Test nakshatra name retrieval"""
        # Get name for Ashwini (index 0)
        result = get_nak_name(0, 'en')
        self.assertEqual(result, 'Ashwini')
    
    def test_get_planet_name(self):
        """Test planet name retrieval"""
        # Get English name for Sun
        result = get_planet_name('Sun', 'en')
        self.assertEqual(result, 'Sun')
        
        # Get Tamil name for Sun
        result = get_planet_name('Sun', 'ta')
        self.assertEqual(result, 'சூரியன்')
    
    def test_constants_exist(self):
        """Test that constants are properly defined"""
        self.assertTrue(len(LUCKY_NUMS) > 0)
        self.assertTrue(len(LUCKY_COLORS) > 0)
        self.assertEqual(len(RASIS), 12)
        self.assertEqual(len(NAKS), 27)


class TestAppEndpoints(unittest.TestCase):
    """Test suite for Flask app endpoints"""
    
    def setUp(self):
        """Set up Flask test client"""
        from app import app
        self.app = app
        self.client = app.test_client()
    
    def test_ping_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/api/ping')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('service', data)
    
    def test_ping_options(self):
        """Test CORS preflight request"""
        response = self.client.options('/api/ping')
        self.assertEqual(response.status_code, 204)


if __name__ == '__main__':
    unittest.main()