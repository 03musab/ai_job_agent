import gevent.monkey
gevent.monkey.patch_all() # This patches everything by default, including subprocess
from dotenv import load_dotenv
load_dotenv()
import logging
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
import time
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_edge_driver_with_manager(headless=True):
    """Test Edge WebDriver using WebDriver Manager for automatic driver management"""
    logger.info(f"Attempting to launch Edge WebDriver with auto-managed driver (headless={headless})...")
    driver = None
    try:
        # Use WebDriver Manager to automatically download and manage the driver
        logger.info("Installing/updating EdgeDriver automatically...")
        driver_path = EdgeChromiumDriverManager().install()
        logger.info(f"Driver ready at: {driver_path}")
        
        # Set up Edge options
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
        
        # Create service with the auto-managed driver
        service = EdgeService(executable_path=driver_path)
        
        # Start the WebDriver
        driver = webdriver.Edge(service=service, options=options)
        logger.info("✅ WebDriver launched successfully!")
        
        # Try to open a simple page to confirm functionality
        logger.info("Navigating to google.com...")
        driver.get("http://www.google.com")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
        logger.info(f"✅ Successfully loaded Google. Page title: {driver.title}")
        return True
        
    except WebDriverException as e:
        logger.error(f"❌ WebDriver failed to launch: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False
    finally:
        if driver:
            driver.quit()
            logger.info("WebDriver closed.")

def test_edge_driver_legacy(headless=True):
    """Test the old method with manual driver path (for comparison)"""
    logger.info(f"Testing legacy method with manual driver path (headless={headless})...")
    driver = None
    try:
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        
        # Check if the manual driver exists
        manual_driver_path = r"C:\WebDrivers\msedgedriver.exe"
        if not os.path.exists(manual_driver_path):
            logger.error(f"❌ Manual driver not found at: {manual_driver_path}")
            return False
            
        service = EdgeService(executable_path=manual_driver_path)
        driver = webdriver.Edge(service=service, options=options)
        
        logger.info("✅ Legacy method worked!")
        driver.get("http://www.google.com")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
        logger.info(f"✅ Successfully loaded Google with legacy method. Page title: {driver.title}")
        return True
        
    except WebDriverException as e:
        logger.error(f"❌ Legacy method failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Legacy method unexpected error: {e}")
        return False
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    logger.info("🚀 Starting Enhanced WebDriver Tests")
    logger.info("=" * 50)
    
    # Test 1: WebDriver Manager (Recommended)
    logger.info("\n📦 TEST 1: Using WebDriver Manager (Auto-managed)")
    logger.info("-" * 50)
    
    logger.info("🔍 Testing non-headless mode...")
    if test_edge_driver_with_manager(headless=False):
        logger.info("✅ Non-headless test PASSED with WebDriver Manager")
    else:
        logger.error("❌ Non-headless test FAILED with WebDriver Manager")
    
    logger.info("\n🔍 Testing headless mode...")
    if test_edge_driver_with_manager(headless=True):
        logger.info("✅ Headless test PASSED with WebDriver Manager")
    else:
        logger.error("❌ Headless test FAILED with WebDriver Manager")
    
    # Test 2: Legacy Method (For comparison)
    logger.info("\n🛠️  TEST 2: Legacy Method (Manual driver path)")
    logger.info("-" * 50)
    
    logger.info("🔍 Testing legacy method...")
    if test_edge_driver_legacy(headless=True):
        logger.info("✅ Legacy method still works")
    else:
        logger.error("❌ Legacy method failed (expected if driver is missing/incompatible)")
    
    logger.info("\n🎉 All tests completed!")
    logger.info("=" * 50)
    logger.info("💡 RECOMMENDATION: Use WebDriver Manager for automatic driver management")
    logger.info("   It will automatically download and manage the correct driver version!")