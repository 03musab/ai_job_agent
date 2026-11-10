# 🛡️ Automated Security Audit Report

> **Status:** 🔴 **Action Required**  
> **Generated:** `2026-11-10 09:02:14 UTC`  
> **Branch/Ref:** `main` (`42d3210e`)  

## 📊 Executive Summary

| Category | Findings | Severity Note |
| :--- | :--- | :--- |
| **🚨 High Severity (Code)** | `9` | Critical flaws, injection, or hardcoded secrets |
| **⚠️ Medium Severity (Code)** | `8` | Weak crypto, insecure configs, or unvalidated parameters |
| **ℹ️ Low Severity (Code)** | `30` | Information leaks or minor code hygiene warnings |
| **📦 Known CVEs (Dependencies)** | `0` | Vulnerabilities identified in third-party packages |
| **Total Security Items** | `47` | Combined code & dependency signals |

## 🔍 Code Security Vulnerabilities (SAST)

Identified `47` code security items across Python source files:

### 1. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:1137`](./app.py#L1137)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
1136         norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}|{user_id}"
1137         job_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
1138
```

### 2. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:1870`](./app.py#L1870)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
1869                 norm = f"{normalize_for_hash(title)}|{normalize_for_hash(company)}|{normalize_for_hash(location)}|{user_id}"
1870                 new_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
1871                 if new_hash != old_hash:
```

### 3. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:3881`](./app.py#L3881)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
3880             norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}"
3881             key = hashlib.md5(norm.encode('utf-8')).hexdigest()
3882             if key not in unique_jobs or job.relevance_score > unique_jobs[key].relevance_score:
```

### 4. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6190`](./app.py#L6190)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6189                     if not processed_row.get('linkedin_url') and processed_row.get('email'):
6190                         email_hash = hashlib.md5(str(processed_row['email']).lower().encode()).hexdigest()
6191                         processed_row['linkedin_url'] = f"csv-upload-{email_hash}"
```

### 5. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6488`](./app.py#L6488)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6487                             if contact_data.get('email'):
6488                                 email_hash = hashlib.md5(contact_data['email'].lower().encode()).hexdigest()
6489                                 contact_data['linkedin_url'] = f"repo-{email_hash}"
```

### 6. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6492`](./app.py#L6492)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6491                                 unique_str = f"{contact_data.get('full_name')}-{contact_data.get('company')}"
6492                                 unique_hash = hashlib.md5(unique_str.encode()).hexdigest()
6493                                 contact_data['linkedin_url'] = f"repo-noemail-{unique_hash}"
```

### 7. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6604`](./app.py#L6604)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6603     if not linkedin_url:
6604         email_hash = hashlib.md5(data['email'].lower().encode()).hexdigest()
6605         linkedin_url = f"manual-entry-{email_hash}"
```

### 8. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6677`](./app.py#L6677)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6676                 if not processed_row.get('linkedin_url') and processed_row.get('email'):
6677                     email_hash = hashlib.md5(processed_row['email'].lower().encode()).hexdigest()
6678                     processed_row['linkedin_url'] = f"csv-import-{email_hash}"
```

### 9. [🚨 HIGH] A Flask app appears to be run with debug=True, which exposes the Werkzeug debugger and allows the execution of arbitrary code.
- **File:** [`./app.py:8916`](./app.py#L8916)
- **Rule ID:** `B201` (flask_debug_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b201_flask_debug_true.html)

```python
8915         logger.warning(f"Could not automatically open browser: {e}")
8916     app.run(debug=True, host='0.0.0.0', port=5000)
```

### 10. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1227`](./app.py#L1227)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1226         """
1227         query = f"SELECT {query_columns} FROM jobs WHERE (user_id = ? OR user_id = 15 OR user_id IS NULL OR posted_by_recruiter_id IS NOT NULL)"
1228         params = [user_id]
```

### 11. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1283`](./app.py#L1283)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1282 
1283         count_query = f"SELECT COUNT(*) FROM ({query})"
1284         cursor.execute(count_query, params)
```

### 12. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1466`](./app.py#L1466)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1465             placeholders = ','.join(['?'] * len(job_ids))
1466             cursor.execute(f"DELETE FROM jobs WHERE id IN ({placeholders}) AND user_id = ?", (*job_ids, user_id))
1467             deleted_count = cursor.rowcount
```

### 13. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:2821`](./app.py#L2821)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
2820 
2821         search_query = f"SELECT * FROM global_hiring_contacts WHERE {' OR '.join(where_clauses)}"
2822         cursor.execute(search_query, params)
```

### 14. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:4302`](./app.py#L4302)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
4301             with open('token.pickle', 'rb') as token:
4302                 creds = pickle.load(token)
4303
```

### 15. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:4788`](./app.py#L4788)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
4787             with open('token.pickle', 'rb') as token:
4788                 creds = pickle.load(token)
4789
```

### 16. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./app.py:8916`](./app.py#L8916)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
8915         logger.warning(f"Could not automatically open browser: {e}")
8916     app.run(debug=True, host='0.0.0.0', port=5000)
```

### 17. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./send_launch_emails.py:163`](./send_launch_emails.py#L163)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
162     with open(token_path, "rb") as token:
163         creds = pickle.load(token)
164
```

### 18. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:23`](./ai_utils.py#L23)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
22         return json.loads(text)
23     except Exception:
24         pass
25
```

### 19. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./ai_utils.py:37`](./ai_utils.py#L37)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
36             return json.loads(cand)
37         except Exception:
38             continue
39
```

### 20. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:47`](./ai_utils.py#L47)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
46             return json.loads(sub)
47         except Exception:
48             pass
49
```

### 21. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:57`](./ai_utils.py#L57)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
56             return json.loads(sub)
57         except Exception:
58             pass
59
```

### 22. [ℹ️ LOW] Consider possible security implications associated with pickle module.
- **File:** [`./app.py:10`](./app.py#L10)
- **Rule ID:** `B403` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b403-import-pickle)

```python
9 import os
10 import pickle
11 import random
```

### 23. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:2130`](./app.py#L2130)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
2129                     date_counts[dt_part] = date_counts.get(dt_part, 0) + 1
2130                 except Exception:
2131                     continue
2132
```

### 24. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2687`](./app.py#L2687)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2686                         ''', (user_id, dt['template_name'], dt['subject'], dt['body'], now_str))
2687                     except Exception:
2688                         pass
2689                 conn.commit()
```

### 25. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2879`](./app.py#L2879)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2878                         ))
2879                     except Exception:
2880                         pass
2881                 conn.commit()
```

### 26. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3019`](./app.py#L3019)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3018             options.add_argument('--disable-dev-shm-usage')
3019             random_user_agent = random.choice(USER_AGENTS)
3020             options.add_argument(f"user-agent={random_user_agent}")
```

### 27. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3241`](./app.py#L3241)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3240             }
3241             headers = {'User-Agent': random.choice(USER_AGENTS)}
3242             try:
```

### 28. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3244`](./app.py#L3244)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3243                 logger.info(f"[LinkedIn] Sending request to LinkedIn for job list (page {page + 1})...")
3244                 time.sleep(random.uniform(*self.request_delay))  # Dynamic delay based on scan mode
3245                 response = requests.get(base_url, params=params, headers=headers, timeout=15, proxies=proxies)
```

### 29. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3312`](./app.py#L3312)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3311                         logger.info(f"[LinkedIn] Fetching job detail page: {job['link']}")
3312                         detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
3313                         time.sleep(random.uniform(2.5, 5.5)) # Increased delay to avoid 429 errors
```

### 30. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3313`](./app.py#L3313)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3312                         detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
3313                         time.sleep(random.uniform(2.5, 5.5)) # Increased delay to avoid 429 errors
3314                         resp = requests.get(job['link'], headers=detail_headers, timeout=15)
```

### 31. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3390`](./app.py#L3390)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3389             session.headers.update({
3390                 'User-Agent': random.choice(USER_AGENTS),
3391                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
```

### 32. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3412`](./app.py#L3412)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3411                     # Randomized delay to avoid detection
3412                     time.sleep(random.uniform(*self.request_delay))
3413
```

### 33. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3612`](./app.py#L3612)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3611             # Randomized delay
3612             time.sleep(random.uniform(1.5, 3.5))
3613
```

### 34. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3615`](./app.py#L3615)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3614             headers = {
3615                 'User-Agent': random.choice(USER_AGENTS),
3616                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
```

### 35. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:4888`](./app.py#L4888)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
4887                                 row[rel_col-1].value = f"🔴 {val}"
4888                         except:
4889                             continue
4890                 # --- Make Links Clickable and Button Style ---
```

### 36. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:5470`](./app.py#L5470)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
5469                 logger.info(f"Cleaned up Excel report: {excel_file}.")
5470             except Exception:
5471                 pass
5472
```

### 37. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:5855`](./app.py#L5855)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
5854                         experience_summary = f"experience as {role}" + (f" at {comp}" if comp else "")
5855             except Exception:
5856                 pass
5857
```

### 38. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:6988`](./app.py#L6988)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
6987         conn.close()
6988     except Exception as e:
6989         pass
6990
```

### 39. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:7354`](./app.py#L7354)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
7353     fake_analysis_data = {
7354         "monthly_visits": f"{random.randint(50, 500)}K",
7355         "bounce_rate": f"{random.randint(30, 70)}%",
```

### 40. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:7355`](./app.py#L7355)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
7354         "monthly_visits": f"{random.randint(50, 500)}K",
7355         "bounce_rate": f"{random.randint(30, 70)}%",
7356         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
```

### 41. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:7356`](./app.py#L7356)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
7355         "bounce_rate": f"{random.randint(30, 70)}%",
7356         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
7357     }
```

### 42. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:7882`](./app.py#L7882)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
7881                 db.update_job_status_and_notes(job_id, current_user.id, 'applied', notes or 'Applied directly via JobSnap')
7882             except Exception:
7883                 pass
7884             return jsonify({
```

### 43. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:8836`](./app.py#L8836)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
8835                 user_name = user_details.get('full_name')
8836         except: pass
8837
```

### 44. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./outreach_scraper.py:48`](./outreach_scraper.py#L48)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
47         self.session = requests.Session()
48         self.session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
49         self.scraped_domains = set()
```

### 45. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./outreach_scraper.py:108`](./outreach_scraper.py#L108)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
107         # Add random delay to appear more human
108         time.sleep(random.uniform(self.min_delay, self.max_delay))
109
```

### 46. [ℹ️ LOW] Consider possible security implications associated with pickle module.
- **File:** [`./send_launch_emails.py:12`](./send_launch_emails.py#L12)
- **Rule ID:** `B403` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b403-import-pickle)

```python
11 import base64
12 import pickle
13 import argparse
```

### 47. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./send_launch_emails.py:259`](./send_launch_emails.py#L259)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
258         role = c.get("Role_Category", "your domain")
259         ticket_id = c.get("TicketId") or c.get("PassCode") or f"JS-{random.randint(1000, 9999)}"
260         subject = tmpl["subject"].format(name=name, role=role)
```

## 📦 Dependency Vulnerability Scan (CVEs)

✅ **No vulnerable third-party dependencies detected.** All scanned packages comply with published security advisories.
## 🛠️ Security Remediation Guidance

- [ ] **Rotate / Environment Variables**: Ensure all database URLs, API tokens, and JWT secrets are injected via `.env` or GitHub Secrets, never hardcoded in source.
- [ ] **Parameterized Queries**: Verify that SQL queries in `app.py` use SQLAlchemy ORM or bound parameters (`db.session.execute(text(...), {'param': val})`).
- [ ] **Dependency Patching**: Run `pip install --upgrade <package>` to bump flagged libraries to their recommended patch versions.
- [ ] **CSRF & Session Hardening**: Ensure `WTF_CSRF_ENABLED=True` and secure cookie flags (`SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`) are active.

---
*This report is automatically generated and updated on each push and scheduled audit by the AI JobSnap Security Agent workflow.*
