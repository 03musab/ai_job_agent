import re
from typing import Dict, List, Optional


CURRENT_YEAR = 2026
MIN_FOUNDED_YEAR = 1800
COMPANY_NAME_MIN_LEN = 2
COMPANY_NAME_MAX_LEN = 100
DESCRIPTION_MAX_LEN = 500

URL_PATTERN = re.compile(
    r'^https?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE,
)


def validate_company(data: Dict) -> List[str]:
    errors: List[str] = []

    company_name = (data.get('company_name') or '').strip()
    if not company_name:
        errors.append('Company name is required.')
    elif not (COMPANY_NAME_MIN_LEN <= len(company_name) <= COMPANY_NAME_MAX_LEN):
        errors.append(f'Company name must be between {COMPANY_NAME_MIN_LEN} and {COMPANY_NAME_MAX_LEN} characters.')

    description = (data.get('description') or '').strip()
    if description and len(description) > DESCRIPTION_MAX_LEN:
        errors.append(f'Description must be at most {DESCRIPTION_MAX_LEN} characters.')

    website = (data.get('website') or '').strip()
    if website and not URL_PATTERN.match(website):
        errors.append('Website must be a valid URL starting with http:// or https://.')

    linkedin = (data.get('linkedin') or '').strip()
    if linkedin and not URL_PATTERN.match(linkedin):
        errors.append('LinkedIn must be a valid URL starting with http:// or https://.')

    founded = data.get('founded')
    if founded is not None:
        try:
            founded_int = int(founded)
        except (ValueError, TypeError):
            errors.append('Founded must be a valid year (integer).')
            founded_int = None
        if founded_int is not None and not (MIN_FOUNDED_YEAR <= founded_int <= CURRENT_YEAR):
            errors.append(f'Founded year must be between {MIN_FOUNDED_YEAR} and {CURRENT_YEAR}.')

    return errors


def is_valid_url(url: str) -> bool:
    if not url:
        return True
    return bool(URL_PATTERN.match(url.strip()))


def sanitize_company_data(data: Dict) -> Dict:
    result = {}
    for key in ('company_name', 'logo', 'website', 'description',
                'industry', 'company_size', 'headquarters', 'linkedin'):
        result[key] = (data.get(key) or '').strip()

    founded = data.get('founded')
    if founded is not None and founded != '':
        try:
            result['founded'] = int(founded)
        except (ValueError, TypeError):
            result['founded'] = None
    else:
        result['founded'] = None

    return result
