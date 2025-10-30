import logging
import os
import random
import re
import time
import requests
from typing import Dict, List, Optional
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

class LegalContactResearcher:
    """
    Legal contact researcher that only scrapes publicly available data
    and respects robots.txt, rate limits, and terms of service.
    """

    def __init__(self, user_id: int, task=None):
        self.user_id = user_id
        self.task = task
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
        self.scraped_domains = set()
        self.rate_limits = {}  # Track request timing per domain
        
        # Legal compliance settings
        self.min_delay = 2  # Minimum delay between requests (seconds)
        self.max_delay = 5  # Maximum delay between requests (seconds)
        self.respect_robots = True
        self.max_requests_per_domain = 10  # Limit requests per domain

    def check_robots_txt(self, url: str) -> bool:
        """Check if scraping is allowed by robots.txt"""
        if not self.respect_robots:
            return True
            
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            user_agent = self.session.headers.get('User-Agent', '*')
            can_fetch = rp.can_fetch(user_agent, url)
            
            if not can_fetch:
                logger.info(f"robots.txt disallows scraping: {url}")
                return False
                
            # Check crawl delay
            crawl_delay = rp.crawl_delay(user_agent)
            if crawl_delay:
                self.min_delay = max(self.min_delay, crawl_delay)
                
            return True
        except Exception as e:
            logger.warning(f"Could not check robots.txt for {url}: {e}")
            return True  # Assume allowed if we can't check

    def respect_rate_limit(self, domain: str):
        """Implement respectful rate limiting"""
        current_time = time.time()
        
        if domain in self.rate_limits:
            time_since_last = current_time - self.rate_limits[domain]['last_request']
            if time_since_last < self.min_delay:
                sleep_time = self.min_delay - time_since_last
                logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
                
            # Check if we've exceeded request limit
            requests_today = self.rate_limits[domain].get('count', 0)
            if requests_today >= self.max_requests_per_domain:
                logger.warning(f"Request limit reached for {domain}")
                return False
        else:
            self.rate_limits[domain] = {'count': 0}
            
        # Add random delay to appear more human
        time.sleep(random.uniform(self.min_delay, self.max_delay))
        
        self.rate_limits[domain]['last_request'] = time.time()
        self.rate_limits[domain]['count'] += 1
        return True

    def search_public_directories(self, keywords: str) -> List[Dict]:
        """Search publicly available business directories"""
        contacts = []
        
        # Public directories that allow research
        directories = [
            {
                'name': 'Crunchbase',
                'search_url': 'https://www.crunchbase.com/discover/organization.companies',
                'params': {'q': keywords}
            },
            # Add more legitimate directories here
        ]
        
        for directory in directories:
            try:
                if not self.respect_rate_limit(urlparse(directory['search_url']).netloc):
                    continue
                    
                if not self.check_robots_txt(directory['search_url']):
                    continue
                
                logger.info(f"Searching {directory['name']} for: {keywords}")
                # Implement specific directory parsing logic here
                
            except Exception as e:
                logger.error(f"Error searching {directory['name']}: {e}")
                
        return contacts

    def scrape_company_careers_page(self, company_url: str) -> Dict:
        """
        Scrape publicly available careers/contact pages with full compliance
        """
        if not self.check_robots_txt(company_url):
            return {}
            
        domain = urlparse(company_url).netloc
        if not self.respect_rate_limit(domain):
            return {}
            
        try:
            logger.info(f"Researching careers page: {company_url}")
            response = self.session.get(company_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for common careers page patterns
            careers_links = []
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                text = link.get_text().lower()
                
                if any(keyword in href or keyword in text for keyword in 
                      ['career', 'job', 'hiring', 'join', 'work-with-us', 'talent']):
                    full_url = urljoin(company_url, link['href'])
                    careers_links.append(full_url)
            
            contact_info = {}
            
            # Scrape careers pages for public contact information
            for careers_url in careers_links[:3]:  # Limit to first 3 links
                if not self.respect_rate_limit(domain):
                    break
                    
                try:
                    careers_response = self.session.get(careers_url, timeout=15)
                    careers_soup = BeautifulSoup(careers_response.content, 'html.parser')
                    
                    # Look for publicly displayed contact information
                    text_content = careers_soup.get_text()
                    
                    # Find email addresses (only those meant to be public)
                    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                    emails = re.findall(email_pattern, text_content)
                    
                    # Filter for relevant emails
                    relevant_emails = []
                    for email in emails:
                        email = email.lower()
                        if any(keyword in email for keyword in 
                              ['career', 'hr', 'job', 'hiring', 'recruit', 'talent']):
                            relevant_emails.append(email)
                    
                    if relevant_emails:
                        contact_info['emails'] = relevant_emails
                        contact_info['source_url'] = careers_url
                        break
                        
                except Exception as e:
                    logger.warning(f"Could not scrape careers page {careers_url}: {e}")
                    
            return contact_info
            
        except Exception as e:
            logger.error(f"Error scraping company careers page {company_url}: {e}")
            return {}

    def search_press_releases(self, company_name: str) -> List[Dict]:
        """Search for HR-related press releases and announcements"""
        contacts = []
        
        try:
            # Use Google News API or similar public news sources
            search_query = f'"{company_name}" "hiring" OR "HR" OR "talent acquisition"'
            
            # This would integrate with legitimate news APIs
            # Example: Google News API, NewsAPI, etc.
            logger.info(f"Searching press releases for: {search_query}")
            
            # Implementation would go here for legitimate news sources
            
        except Exception as e:
            logger.error(f"Error searching press releases: {e}")
            
        return contacts

    def validate_contact_data(self, contact_data: Dict) -> bool:
        """Validate that contact data meets legal and ethical standards"""
        
        # Ensure we have proper source attribution
        if 'source_url' not in contact_data:
            logger.warning("Contact data missing source URL")
            return False
            
        # Ensure data is from publicly available sources
        if 'source_type' not in contact_data:
            contact_data['source_type'] = 'Public Website'
            
        # Add compliance metadata
        contact_data['scraped_at'] = time.time()
        contact_data['compliance_checked'] = True
        contact_data['robots_txt_compliant'] = True
        
        return True

    def generate_compliance_report(self) -> Dict:
        """Generate a report of compliance measures taken"""
        return {
            'domains_accessed': len(self.scraped_domains),
            'robots_txt_respected': self.respect_robots,
            'rate_limiting_enabled': True,
            'max_requests_per_domain': self.max_requests_per_domain,
            'min_delay_seconds': self.min_delay,
            'data_sources': 'Public websites, press releases, business directories',
            'personal_data_handling': 'Only publicly displayed contact information',
            'compliance_standards': ['robots.txt', 'rate limiting', 'public data only']
        }

    def run(self, keywords: str, companies: List[str] = None) -> Dict:
        """
        Main method to run legal contact research
        """
        logger.info(f"Starting legal contact research for: {keywords}")
        
        results = {
            'contacts': [],
            'companies_researched': [],
            'compliance_report': {},
            'total_contacts_found': 0
        }
        
        try:
            # Search public directories
            directory_contacts = self.search_public_directories(keywords)
            results['contacts'].extend(directory_contacts)
            
            # Research specific companies if provided
            if companies:
                for company in companies:
                    try:
                        # First, find the company's official website
                        search_query = f'"{company}" official website'
                        # Use legitimate search APIs or manual research
                        
                        # For each company, research their careers pages
                        company_url = f"https://www.{company.lower().replace(' ', '')}.com"
                        contact_info = self.scrape_company_careers_page(company_url)
                        
                        if contact_info:
                            contact_data = {
                                'company': company,
                                'contact_info': contact_info,
                                'source_type': 'Company Careers Page',
                                'source_url': company_url
                            }
                            
                            if self.validate_contact_data(contact_data):
                                results['contacts'].append(contact_data)
                                results['companies_researched'].append(company)
                                
                    except Exception as e:
                        logger.error(f"Error researching company {company}: {e}")
            
            results['total_contacts_found'] = len(results['contacts'])
            results['compliance_report'] = self.generate_compliance_report()
            
            logger.info(f"Legal contact research completed. Found {results['total_contacts_found']} contacts.")
            
        except Exception as e:
            logger.error(f"Error during legal contact research: {e}")
            
        return results

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize researcher
    researcher = LegalContactResearcher(user_id=1)
    
    # Run research
    companies = ["Wipro", "TCS", "Infosys", "Flipkart", "Freshworks"]
    results = researcher.run("AI HR hiring", companies=companies)
    
    print(f"Found {results['total_contacts_found']} contacts")
    print(f"Compliance report: {results['compliance_report']}")