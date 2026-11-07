# 🛡️ Automated Security Audit Report

> **Status:** 🔴 **Action Required**  
> **Generated:** `2026-11-07 20:37:35 UTC`  
> **Branch/Ref:** `main` (`Local Wo`)  

## 📊 Executive Summary

| Category | Findings | Severity Note |
| :--- | :--- | :--- |
| **🚨 High Severity (Code)** | `9` | Critical flaws, injection, or hardcoded secrets |
| **⚠️ Medium Severity (Code)** | `8` | Weak crypto, insecure configs, or unvalidated parameters |
| **ℹ️ Low Severity (Code)** | `30` | Information leaks or minor code hygiene warnings |
| **📦 Known CVEs (Dependencies)** | `360` | Vulnerabilities identified in third-party packages |
| **Total Security Items** | `407` | Combined code & dependency signals |

## 🔍 Code Security Vulnerabilities (SAST)

Identified `47` code security items across Python source files:

### 1. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:1116`](./app.py#L1116)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
1115         norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}|{user_id}"
1116         job_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
1117
```

### 2. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:1849`](./app.py#L1849)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
1848                 norm = f"{normalize_for_hash(title)}|{normalize_for_hash(company)}|{normalize_for_hash(location)}|{user_id}"
1849                 new_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
1850                 if new_hash != old_hash:
```

### 3. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:3860`](./app.py#L3860)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
3859             norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}"
3860             key = hashlib.md5(norm.encode('utf-8')).hexdigest()
3861             if key not in unique_jobs or job.relevance_score > unique_jobs[key].relevance_score:
```

### 4. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6153`](./app.py#L6153)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6152                     if not processed_row.get('linkedin_url') and processed_row.get('email'):
6153                         email_hash = hashlib.md5(str(processed_row['email']).lower().encode()).hexdigest()
6154                         processed_row['linkedin_url'] = f"csv-upload-{email_hash}"
```

### 5. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6451`](./app.py#L6451)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6450                             if contact_data.get('email'):
6451                                 email_hash = hashlib.md5(contact_data['email'].lower().encode()).hexdigest()
6452                                 contact_data['linkedin_url'] = f"repo-{email_hash}"
```

### 6. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6455`](./app.py#L6455)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6454                                 unique_str = f"{contact_data.get('full_name')}-{contact_data.get('company')}"
6455                                 unique_hash = hashlib.md5(unique_str.encode()).hexdigest()
6456                                 contact_data['linkedin_url'] = f"repo-noemail-{unique_hash}"
```

### 7. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6567`](./app.py#L6567)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6566     if not linkedin_url:
6567         email_hash = hashlib.md5(data['email'].lower().encode()).hexdigest()
6568         linkedin_url = f"manual-entry-{email_hash}"
```

### 8. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6640`](./app.py#L6640)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6639                 if not processed_row.get('linkedin_url') and processed_row.get('email'):
6640                     email_hash = hashlib.md5(processed_row['email'].lower().encode()).hexdigest()
6641                     processed_row['linkedin_url'] = f"csv-import-{email_hash}"
```

### 9. [🚨 HIGH] A Flask app appears to be run with debug=True, which exposes the Werkzeug debugger and allows the execution of arbitrary code.
- **File:** [`./app.py:8879`](./app.py#L8879)
- **Rule ID:** `B201` (flask_debug_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b201_flask_debug_true.html)

```python
8878         logger.warning(f"Could not automatically open browser: {e}")
8879     app.run(debug=True, host='0.0.0.0', port=5000)
```

### 10. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1206`](./app.py#L1206)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1205         """
1206         query = f"SELECT {query_columns} FROM jobs WHERE (user_id = ? OR user_id = 15 OR user_id IS NULL OR posted_by_recruiter_id IS NOT NULL)"
1207         params = [user_id]
```

### 11. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1262`](./app.py#L1262)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1261 
1262         count_query = f"SELECT COUNT(*) FROM ({query})"
1263         cursor.execute(count_query, params)
```

### 12. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1445`](./app.py#L1445)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1444             placeholders = ','.join(['?'] * len(job_ids))
1445             cursor.execute(f"DELETE FROM jobs WHERE id IN ({placeholders}) AND user_id = ?", (*job_ids, user_id))
1446             deleted_count = cursor.rowcount
```

### 13. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:2800`](./app.py#L2800)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
2799 
2800         search_query = f"SELECT * FROM global_hiring_contacts WHERE {' OR '.join(where_clauses)}"
2801         cursor.execute(search_query, params)
```

### 14. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:4281`](./app.py#L4281)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
4280             with open('token.pickle', 'rb') as token:
4281                 creds = pickle.load(token)
4282
```

### 15. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:4767`](./app.py#L4767)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
4766             with open('token.pickle', 'rb') as token:
4767                 creds = pickle.load(token)
4768
```

### 16. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./app.py:8879`](./app.py#L8879)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
8878         logger.warning(f"Could not automatically open browser: {e}")
8879     app.run(debug=True, host='0.0.0.0', port=5000)
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
- **File:** [`./app.py:2109`](./app.py#L2109)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
2108                     date_counts[dt_part] = date_counts.get(dt_part, 0) + 1
2109                 except Exception:
2110                     continue
2111
```

### 24. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2666`](./app.py#L2666)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2665                         ''', (user_id, dt['template_name'], dt['subject'], dt['body'], now_str))
2666                     except Exception:
2667                         pass
2668                 conn.commit()
```

### 25. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2858`](./app.py#L2858)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2857                         ))
2858                     except Exception:
2859                         pass
2860                 conn.commit()
```

### 26. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:2998`](./app.py#L2998)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
2997             options.add_argument('--disable-dev-shm-usage')
2998             random_user_agent = random.choice(USER_AGENTS)
2999             options.add_argument(f"user-agent={random_user_agent}")
```

### 27. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3220`](./app.py#L3220)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3219             }
3220             headers = {'User-Agent': random.choice(USER_AGENTS)}
3221             try:
```

### 28. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3223`](./app.py#L3223)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3222                 logger.info(f"[LinkedIn] Sending request to LinkedIn for job list (page {page + 1})...")
3223                 time.sleep(random.uniform(*self.request_delay))  # Dynamic delay based on scan mode
3224                 response = requests.get(base_url, params=params, headers=headers, timeout=15, proxies=proxies)
```

### 29. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3291`](./app.py#L3291)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3290                         logger.info(f"[LinkedIn] Fetching job detail page: {job['link']}")
3291                         detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
3292                         time.sleep(random.uniform(2.5, 5.5)) # Increased delay to avoid 429 errors
```

### 30. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3292`](./app.py#L3292)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3291                         detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
3292                         time.sleep(random.uniform(2.5, 5.5)) # Increased delay to avoid 429 errors
3293                         resp = requests.get(job['link'], headers=detail_headers, timeout=15)
```

### 31. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3369`](./app.py#L3369)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3368             session.headers.update({
3369                 'User-Agent': random.choice(USER_AGENTS),
3370                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
```

### 32. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3391`](./app.py#L3391)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3390                     # Randomized delay to avoid detection
3391                     time.sleep(random.uniform(*self.request_delay))
3392
```

### 33. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3591`](./app.py#L3591)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3590             # Randomized delay
3591             time.sleep(random.uniform(1.5, 3.5))
3592
```

### 34. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3594`](./app.py#L3594)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3593             headers = {
3594                 'User-Agent': random.choice(USER_AGENTS),
3595                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
```

### 35. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:4867`](./app.py#L4867)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
4866                                 row[rel_col-1].value = f"🔴 {val}"
4867                         except:
4868                             continue
4869                 # --- Make Links Clickable and Button Style ---
```

### 36. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:5449`](./app.py#L5449)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
5448                 logger.info(f"Cleaned up Excel report: {excel_file}.")
5449             except Exception:
5450                 pass
5451
```

### 37. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:5825`](./app.py#L5825)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
5824                         experience_summary = f"experience as {role}" + (f" at {comp}" if comp else "")
5825             except Exception:
5826                 pass
5827
```

### 38. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:6951`](./app.py#L6951)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
6950         conn.close()
6951     except Exception as e:
6952         pass
6953
```

### 39. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:7317`](./app.py#L7317)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
7316     fake_analysis_data = {
7317         "monthly_visits": f"{random.randint(50, 500)}K",
7318         "bounce_rate": f"{random.randint(30, 70)}%",
```

### 40. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:7318`](./app.py#L7318)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
7317         "monthly_visits": f"{random.randint(50, 500)}K",
7318         "bounce_rate": f"{random.randint(30, 70)}%",
7319         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
```

### 41. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:7319`](./app.py#L7319)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
7318         "bounce_rate": f"{random.randint(30, 70)}%",
7319         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
7320     }
```

### 42. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:7845`](./app.py#L7845)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
7844                 db.update_job_status_and_notes(job_id, current_user.id, 'applied', notes or 'Applied directly via JobSnap')
7845             except Exception:
7846                 pass
7847             return jsonify({
```

### 43. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:8799`](./app.py#L8799)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
8798                 user_name = user_details.get('full_name')
8799         except: pass
8800
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

Found `360` unique CVE advisories across dependencies:

| Package | Installed Version | Advisory / CVE | Suggested Remediation Version |
| :--- | :--- | :--- | :--- |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2097`](https://osv.dev/vulnerability/PYSEC-2026-2097) | `3.13.4` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2095`](https://osv.dev/vulnerability/PYSEC-2026-2095) | `3.13.4` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2098`](https://osv.dev/vulnerability/PYSEC-2026-2098) | `3.13.4` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2099`](https://osv.dev/vulnerability/PYSEC-2026-2099) | `3.13.4` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2101`](https://osv.dev/vulnerability/PYSEC-2026-2101) | `3.13.4` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2100`](https://osv.dev/vulnerability/PYSEC-2026-2100) | `3.13.4` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2102`](https://osv.dev/vulnerability/PYSEC-2026-2102) | `3.13.4` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-1100`](https://osv.dev/vulnerability/PYSEC-2026-1100) | `3.13.3` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-1101`](https://osv.dev/vulnerability/PYSEC-2026-1101) | `3.13.3` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-1104`](https://osv.dev/vulnerability/PYSEC-2026-1104) | `3.12.14` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2103`](https://osv.dev/vulnerability/PYSEC-2026-2103) | `3.13.4` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-1099`](https://osv.dev/vulnerability/PYSEC-2026-1099) | `3.13.3` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-1106`](https://osv.dev/vulnerability/PYSEC-2026-1106) | `3.13.3` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-1105`](https://osv.dev/vulnerability/PYSEC-2026-1105) | `3.13.3` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-1097`](https://osv.dev/vulnerability/PYSEC-2026-1097) | `3.13.3` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-1107`](https://osv.dev/vulnerability/PYSEC-2026-1107) | `3.13.3` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-1109`](https://osv.dev/vulnerability/PYSEC-2026-1109) | `3.13.3` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2094`](https://osv.dev/vulnerability/PYSEC-2026-2094) | `3.13.4` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2096`](https://osv.dev/vulnerability/PYSEC-2026-2096) | `3.13.4` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2104`](https://osv.dev/vulnerability/PYSEC-2026-2104) | `3.14.0` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2105`](https://osv.dev/vulnerability/PYSEC-2026-2105) | `3.14.0` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2107`](https://osv.dev/vulnerability/PYSEC-2026-2107) | `3.14.1` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2112`](https://osv.dev/vulnerability/PYSEC-2026-2112) | `3.14.1` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2110`](https://osv.dev/vulnerability/PYSEC-2026-2110) | `3.14.1` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2106`](https://osv.dev/vulnerability/PYSEC-2026-2106) | `3.14.0` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2109`](https://osv.dev/vulnerability/PYSEC-2026-2109) | `3.14.1` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2111`](https://osv.dev/vulnerability/PYSEC-2026-2111) | `3.14.1` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2113`](https://osv.dev/vulnerability/PYSEC-2026-2113) | `3.14.1` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-2108`](https://osv.dev/vulnerability/PYSEC-2026-2108) | `3.14.1` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-237`](https://osv.dev/vulnerability/PYSEC-2026-237) | `3.14.1` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-3547`](https://osv.dev/vulnerability/PYSEC-2026-3547) | `3.14.2` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-3546`](https://osv.dev/vulnerability/PYSEC-2026-3546) | `3.14.2` |
| **`aiohttp`** | `3.11.18` | [`PYSEC-2026-3545`](https://osv.dev/vulnerability/PYSEC-2026-3545) | `3.14.3` |
| **`aiohttp`** | `3.11.18` | [`CVE-2026-111064`](https://osv.dev/vulnerability/CVE-2026-111064) | `3.14.4` |
| **`aiohttp`** | `3.11.18` | [`GHSA-2g87-pp6c-29x5`](https://osv.dev/vulnerability/GHSA-2g87-pp6c-29x5) | `3.14.4` |
| **`aiohttp`** | `3.11.18` | [`CVE-2026-111063`](https://osv.dev/vulnerability/CVE-2026-111063) | `3.14.4` |
| **`aiohttp`** | `3.11.18` | [`CVE-2026-111750`](https://osv.dev/vulnerability/CVE-2026-111750) | `3.14.4` |
| **`aiohttp`** | `3.11.18` | [`CVE-2026-111066`](https://osv.dev/vulnerability/CVE-2026-111066) | `3.14.4` |
| **`aiohttp`** | `3.11.18` | [`CVE-2026-111749`](https://osv.dev/vulnerability/CVE-2026-111749) | `3.14.4` |
| **`aiohttp`** | `3.11.18` | [`CVE-2026-111065`](https://osv.dev/vulnerability/CVE-2026-111065) | `3.14.4` |
| **`aiohttp`** | `3.11.18` | [`CVE-2026-111748`](https://osv.dev/vulnerability/CVE-2026-111748) | `3.14.4` |
| **`anyio`** | `4.9.0` | [`PYSEC-2026-4025`](https://osv.dev/vulnerability/PYSEC-2026-4025) | `4.14.2` |
| **`anyio`** | `4.9.0` | [`PYSEC-2026-4024`](https://osv.dev/vulnerability/PYSEC-2026-4024) | `4.14.2` |
| **`brotli`** | `1.2.0` | [`PYSEC-2026-4322`](https://osv.dev/vulnerability/PYSEC-2026-4322) | `1.2.1` |
| **`certifi`** | `2025.7.9` | [`PYSEC-2026-4320`](https://osv.dev/vulnerability/PYSEC-2026-4320) | `2026.10.18` |
| **`cryptography`** | `46.0.3` | [`PYSEC-2026-2141`](https://osv.dev/vulnerability/PYSEC-2026-2141) | `46.0.5` |
| **`cryptography`** | `46.0.3` | [`PYSEC-2026-35`](https://osv.dev/vulnerability/PYSEC-2026-35) | `46.0.6` |
| **`cryptography`** | `46.0.3` | [`PYSEC-2026-36`](https://osv.dev/vulnerability/PYSEC-2026-36) | `46.0.7` |
| **`cryptography`** | `46.0.3` | [`PYSEC-2026-3554`](https://osv.dev/vulnerability/PYSEC-2026-3554) | `49.0.0` |
| **`cryptography`** | `46.0.3` | [`PYSEC-2026-3552`](https://osv.dev/vulnerability/PYSEC-2026-3552) | `50.0.0` |
| **`cryptography`** | `46.0.3` | [`PYSEC-2026-3553`](https://osv.dev/vulnerability/PYSEC-2026-3553) | `49.0.0` |
| **`cryptography`** | `46.0.3` | [`GHSA-537c-gmf6-5ccf`](https://osv.dev/vulnerability/GHSA-537c-gmf6-5ccf) | `48.0.1` |
| **`django`** | `5.1.5` | [`PYSEC-2025-13`](https://osv.dev/vulnerability/PYSEC-2025-13) | `4.2.20, 5.0.13, 5.1.7` |
| **`django`** | `5.1.5` | [`PYSEC-2025-37`](https://osv.dev/vulnerability/PYSEC-2025-37) | `4.2.21, 5.1.9, 5.2.1` |
| **`django`** | `5.1.5` | [`PYSEC-2025-14`](https://osv.dev/vulnerability/PYSEC-2025-14) | `5.0.14, 5.1.8` |
| **`django`** | `5.1.5` | [`PYSEC-2025-47`](https://osv.dev/vulnerability/PYSEC-2025-47) | `4.2.22, 5.1.10, 5.2.2` |
| **`django`** | `5.1.5` | [`PYSEC-2025-105`](https://osv.dev/vulnerability/PYSEC-2025-105) | `4.2.24, 5.1.12, 5.2.6` |
| **`django`** | `5.1.5` | [`PYSEC-2025-106`](https://osv.dev/vulnerability/PYSEC-2025-106) | `4.2.25, 5.1.13, 5.2.7` |
| **`django`** | `5.1.5` | [`PYSEC-2026-1296`](https://osv.dev/vulnerability/PYSEC-2026-1296) | `4.2.25, 5.1.13, 5.2.7` |
| **`django`** | `5.1.5` | [`PYSEC-2025-107`](https://osv.dev/vulnerability/PYSEC-2025-107) | `4.2.26, 5.1.14, 5.2.8` |
| **`django`** | `5.1.5` | [`PYSEC-2025-108`](https://osv.dev/vulnerability/PYSEC-2025-108) | `4.2.26, 5.1.14, 5.2.8` |
| **`django`** | `5.1.5` | [`PYSEC-2025-104`](https://osv.dev/vulnerability/PYSEC-2025-104) | `4.2.27, 5.1.15, 5.2.9` |
| **`django`** | `5.1.5` | [`PYSEC-2025-109`](https://osv.dev/vulnerability/PYSEC-2025-109) | `4.2.27, 5.1.15, 5.2.9` |
| **`django`** | `5.1.5` | [`PYSEC-2026-3717`](https://osv.dev/vulnerability/PYSEC-2026-3717) | `5.2.17, 6.0.8, 6.1.1` |
| **`django`** | `5.1.5` | [`PYSEC-2026-198`](https://osv.dev/vulnerability/PYSEC-2026-198) | `5.2.15, 6.0.6` |
| **`django`** | `5.1.5` | [`PYSEC-2026-199`](https://osv.dev/vulnerability/PYSEC-2026-199) | `5.2.15, 6.0.6` |
| **`django`** | `5.1.5` | [`PYSEC-2026-201`](https://osv.dev/vulnerability/PYSEC-2026-201) | `5.2.15, 6.0.6` |
| **`django`** | `5.1.5` | [`PYSEC-2026-2090`](https://osv.dev/vulnerability/PYSEC-2026-2090) | `5.2.16, 6.0.7` |
| **`django`** | `5.1.5` | [`PYSEC-2026-2091`](https://osv.dev/vulnerability/PYSEC-2026-2091) | `5.2.16, 6.0.7` |
| **`django`** | `5.1.5` | [`PYSEC-2026-2092`](https://osv.dev/vulnerability/PYSEC-2026-2092) | `5.2.16, 6.0.7` |
| **`django`** | `5.1.5` | [`PYSEC-2026-4035`](https://osv.dev/vulnerability/PYSEC-2026-4035) | `5.2.17, 6.0.8` |
| **`dnspython`** | `2.8.0` | [`CVE-2026-114605`](https://osv.dev/vulnerability/CVE-2026-114605) | `2.9.0` |
| **`filelock`** | `3.18.0` | [`PYSEC-2026-1375`](https://osv.dev/vulnerability/PYSEC-2026-1375) | `3.20.1` |
| **`filelock`** | `3.18.0` | [`PYSEC-2026-1374`](https://osv.dev/vulnerability/PYSEC-2026-1374) | `3.20.3` |
| **`filelock`** | `3.18.0` | [`CVE-2026-112910`](https://osv.dev/vulnerability/CVE-2026-112910) | `4.2.1` |
| **`filelock`** | `3.18.0` | [`CVE-2026-112909`](https://osv.dev/vulnerability/CVE-2026-112909) | `4.2.1` |
| **`flask`** | `3.1.2` | [`PYSEC-2026-2151`](https://osv.dev/vulnerability/PYSEC-2026-2151) | `3.1.3` |
| **`fsspec`** | `2025.3.2` | [`PYSEC-2026-4217`](https://osv.dev/vulnerability/PYSEC-2026-4217) | `2026.6.0` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-2160`](https://osv.dev/vulnerability/PYSEC-2026-2160) | `3.1.47` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-2161`](https://osv.dev/vulnerability/PYSEC-2026-2161) | `3.1.47` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-2163`](https://osv.dev/vulnerability/PYSEC-2026-2163) | `3.1.49` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3984`](https://osv.dev/vulnerability/PYSEC-2026-3984) | `3.1.60` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3980`](https://osv.dev/vulnerability/PYSEC-2026-3980) | `3.1.50` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3982`](https://osv.dev/vulnerability/PYSEC-2026-3982) | `3.1.60` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3981`](https://osv.dev/vulnerability/PYSEC-2026-3981) | `3.1.53` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-2162`](https://osv.dev/vulnerability/PYSEC-2026-2162) | `3.1.48` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3836`](https://osv.dev/vulnerability/PYSEC-2026-3836) | `3.1.51` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3995`](https://osv.dev/vulnerability/PYSEC-2026-3995) | `3.1.54` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3951`](https://osv.dev/vulnerability/PYSEC-2026-3951) | `3.1.55` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3783`](https://osv.dev/vulnerability/PYSEC-2026-3783) | `3.1.58` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3785`](https://osv.dev/vulnerability/PYSEC-2026-3785) | `3.1.59` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3786`](https://osv.dev/vulnerability/PYSEC-2026-3786) | `3.1.59` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3787`](https://osv.dev/vulnerability/PYSEC-2026-3787) | `3.1.59` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3788`](https://osv.dev/vulnerability/PYSEC-2026-3788) | `3.1.59` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3784`](https://osv.dev/vulnerability/PYSEC-2026-3784) | `3.1.58` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3837`](https://osv.dev/vulnerability/PYSEC-2026-3837) | `3.1.59` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3840`](https://osv.dev/vulnerability/PYSEC-2026-3840) | `3.1.58` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3838`](https://osv.dev/vulnerability/PYSEC-2026-3838) | `3.1.58` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3839`](https://osv.dev/vulnerability/PYSEC-2026-3839) | `3.1.51` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3841`](https://osv.dev/vulnerability/PYSEC-2026-3841) | `3.1.58` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3843`](https://osv.dev/vulnerability/PYSEC-2026-3843) | `3.1.58` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3949`](https://osv.dev/vulnerability/PYSEC-2026-3949) | `3.1.57` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3953`](https://osv.dev/vulnerability/PYSEC-2026-3953) | `3.1.54` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3952`](https://osv.dev/vulnerability/PYSEC-2026-3952) | `3.1.54` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3950`](https://osv.dev/vulnerability/PYSEC-2026-3950) | `3.1.56` |
| **`gitpython`** | `3.1.44` | [`PYSEC-2026-3948`](https://osv.dev/vulnerability/PYSEC-2026-3948) | `3.1.57` |
| **`gitpython`** | `3.1.44` | [`CVE-2026-114145`](https://osv.dev/vulnerability/CVE-2026-114145) | `3.2.1` |
| **`gitpython`** | `3.1.44` | [`CVE-2026-110859`](https://osv.dev/vulnerability/CVE-2026-110859) | `3.2.0` |
| **`gitpython`** | `3.1.44` | [`CVE-2026-110858`](https://osv.dev/vulnerability/CVE-2026-110858) | `3.2.0` |
| **`gitpython`** | `3.1.44` | [`CVE-2026-110856`](https://osv.dev/vulnerability/CVE-2026-110856) | `3.2.0` |
| **`gitpython`** | `3.1.44` | [`CVE-2026-110857`](https://osv.dev/vulnerability/CVE-2026-110857) | `3.2.0` |
| **`gitpython`** | `3.1.44` | [`CVE-2026-110855`](https://osv.dev/vulnerability/CVE-2026-110855) | `3.2.0` |
| **`httplib2`** | `0.22.0` | [`PYSEC-2026-3444`](https://osv.dev/vulnerability/PYSEC-2026-3444) | `0.32.0` |
| **`idna`** | `3.10` | [`PYSEC-2026-215`](https://osv.dev/vulnerability/PYSEC-2026-215) | `3.15` |
| **`langsmith`** | `0.2.11` | [`PYSEC-2026-2583`](https://osv.dev/vulnerability/PYSEC-2026-2583) | `0.7.31` |
| **`langsmith`** | `0.2.11` | [`PYSEC-2026-2555`](https://osv.dev/vulnerability/PYSEC-2026-2555) | `0.8.0` |
| **`langsmith`** | `0.2.11` | [`PYSEC-2026-2582`](https://osv.dev/vulnerability/PYSEC-2026-2582) | `0.8.0` |
| **`langsmith`** | `0.2.11` | [`CVE-2026-59152`](https://osv.dev/vulnerability/CVE-2026-59152) | `0.8.18` |
| **`lxml`** | `6.0.2` | [`PYSEC-2026-87`](https://osv.dev/vulnerability/PYSEC-2026-87) | `6.1.0` |
| **`marshmallow`** | `3.26.1` | [`PYSEC-2026-1605`](https://osv.dev/vulnerability/PYSEC-2026-1605) | `3.26.2, 4.1.2` |
| **`oauthlib`** | `3.3.1` | [`PYSEC-2026-4114`](https://osv.dev/vulnerability/PYSEC-2026-4114) | `4.0.0` |
| **`oauthlib`** | `3.3.1` | [`CVE-2026-49272`](https://osv.dev/vulnerability/CVE-2026-49272) | `4.0.1` |
| **`orjson`** | `3.10.16` | [`PYSEC-2026-107`](https://osv.dev/vulnerability/PYSEC-2026-107) | `3.11.6` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-2249`](https://osv.dev/vulnerability/PYSEC-2026-2249) | `12.1.1` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-2250`](https://osv.dev/vulnerability/PYSEC-2026-2250) | `12.2.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-165`](https://osv.dev/vulnerability/PYSEC-2026-165) | `12.2.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-2874`](https://osv.dev/vulnerability/PYSEC-2026-2874) | `12.2.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-2252`](https://osv.dev/vulnerability/PYSEC-2026-2252) | `12.2.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-2253`](https://osv.dev/vulnerability/PYSEC-2026-2253) | `12.3.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-2255`](https://osv.dev/vulnerability/PYSEC-2026-2255) | `12.3.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-2257`](https://osv.dev/vulnerability/PYSEC-2026-2257) | `12.3.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-2256`](https://osv.dev/vulnerability/PYSEC-2026-2256) | `12.3.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-2254`](https://osv.dev/vulnerability/PYSEC-2026-2254) | `12.3.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-3453`](https://osv.dev/vulnerability/PYSEC-2026-3453) | `12.3.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-3451`](https://osv.dev/vulnerability/PYSEC-2026-3451) | `12.3.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-3493`](https://osv.dev/vulnerability/PYSEC-2026-3493) | `12.3.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-3454`](https://osv.dev/vulnerability/PYSEC-2026-3454) | `12.3.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-3494`](https://osv.dev/vulnerability/PYSEC-2026-3494) | `12.3.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-3495`](https://osv.dev/vulnerability/PYSEC-2026-3495) | `12.3.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-3496`](https://osv.dev/vulnerability/PYSEC-2026-3496) | `12.3.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4327`](https://osv.dev/vulnerability/PYSEC-2026-4327) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4326`](https://osv.dev/vulnerability/PYSEC-2026-4326) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4339`](https://osv.dev/vulnerability/PYSEC-2026-4339) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4340`](https://osv.dev/vulnerability/PYSEC-2026-4340) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4343`](https://osv.dev/vulnerability/PYSEC-2026-4343) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4334`](https://osv.dev/vulnerability/PYSEC-2026-4334) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4337`](https://osv.dev/vulnerability/PYSEC-2026-4337) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4341`](https://osv.dev/vulnerability/PYSEC-2026-4341) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4330`](https://osv.dev/vulnerability/PYSEC-2026-4330) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4338`](https://osv.dev/vulnerability/PYSEC-2026-4338) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4335`](https://osv.dev/vulnerability/PYSEC-2026-4335) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4331`](https://osv.dev/vulnerability/PYSEC-2026-4331) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4332`](https://osv.dev/vulnerability/PYSEC-2026-4332) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4329`](https://osv.dev/vulnerability/PYSEC-2026-4329) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`PYSEC-2026-4342`](https://osv.dev/vulnerability/PYSEC-2026-4342) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112895`](https://osv.dev/vulnerability/CVE-2026-112895) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112400`](https://osv.dev/vulnerability/CVE-2026-112400) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112897`](https://osv.dev/vulnerability/CVE-2026-112897) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112395`](https://osv.dev/vulnerability/CVE-2026-112395) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112404`](https://osv.dev/vulnerability/CVE-2026-112404) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112899`](https://osv.dev/vulnerability/CVE-2026-112899) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112900`](https://osv.dev/vulnerability/CVE-2026-112900) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112893`](https://osv.dev/vulnerability/CVE-2026-112893) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112891`](https://osv.dev/vulnerability/CVE-2026-112891) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112390`](https://osv.dev/vulnerability/CVE-2026-112390) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112401`](https://osv.dev/vulnerability/CVE-2026-112401) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112391`](https://osv.dev/vulnerability/CVE-2026-112391) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112894`](https://osv.dev/vulnerability/CVE-2026-112894) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112406`](https://osv.dev/vulnerability/CVE-2026-112406) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112399`](https://osv.dev/vulnerability/CVE-2026-112399) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112892`](https://osv.dev/vulnerability/CVE-2026-112892) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-112393`](https://osv.dev/vulnerability/CVE-2026-112393) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-96638`](https://osv.dev/vulnerability/CVE-2026-96638) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-96640`](https://osv.dev/vulnerability/CVE-2026-96640) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`CVE-2026-96778`](https://osv.dev/vulnerability/CVE-2026-96778) | `13.0.0` |
| **`pillow`** | `11.1.0` | [`GHSA-78g4-xqwv-q3g8`](https://osv.dev/vulnerability/GHSA-78g4-xqwv-q3g8) | `13.0.0` |
| **`pip`** | `26.0.1` | [`PYSEC-2026-2875`](https://osv.dev/vulnerability/PYSEC-2026-2875) | `26.1` |
| **`pip`** | `26.0.1` | [`PYSEC-2026-2876`](https://osv.dev/vulnerability/PYSEC-2026-2876) | `26.1` |
| **`pip`** | `26.0.1` | [`PYSEC-2026-196`](https://osv.dev/vulnerability/PYSEC-2026-196) | `26.1.2` |
| **`pip`** | `26.0.1` | [`PYSEC-2026-3721`](https://osv.dev/vulnerability/PYSEC-2026-3721) | `26.2` |
| **`protobuf`** | `5.29.4` | [`PYSEC-2026-1806`](https://osv.dev/vulnerability/PYSEC-2026-1806) | `4.25.8, 5.29.5, 6.31.1` |
| **`protobuf`** | `5.29.4` | [`PYSEC-2026-1805`](https://osv.dev/vulnerability/PYSEC-2026-1805) | `5.29.6, 6.33.5` |
| **`pyarrow`** | `19.0.1` | [`PYSEC-2026-113`](https://osv.dev/vulnerability/PYSEC-2026-113) | `23.0.1` |
| **`pyasn1`** | `0.6.1` | [`PYSEC-2026-1810`](https://osv.dev/vulnerability/PYSEC-2026-1810) | `0.6.2` |
| **`pyasn1`** | `0.6.1` | [`PYSEC-2026-2263`](https://osv.dev/vulnerability/PYSEC-2026-2263) | `0.6.3` |
| **`pyasn1`** | `0.6.1` | [`PYSEC-2026-3456`](https://osv.dev/vulnerability/PYSEC-2026-3456) | `0.6.4` |
| **`pyasn1`** | `0.6.1` | [`PYSEC-2026-3457`](https://osv.dev/vulnerability/PYSEC-2026-3457) | `0.6.4` |
| **`pyasn1`** | `0.6.1` | [`PYSEC-2026-3455`](https://osv.dev/vulnerability/PYSEC-2026-3455) | `0.6.4` |
| **`pyasn1`** | `0.6.1` | [`CVE-2026-119196`](https://osv.dev/vulnerability/CVE-2026-119196) | `0.6.5` |
| **`pyasn1`** | `0.6.1` | [`CVE-2026-119194`](https://osv.dev/vulnerability/CVE-2026-119194) | `0.6.5` |
| **`pyasn1`** | `0.6.1` | [`CVE-2026-119197`](https://osv.dev/vulnerability/CVE-2026-119197) | `0.6.5` |
| **`pyasn1`** | `0.6.1` | [`CVE-2026-119195`](https://osv.dev/vulnerability/CVE-2026-119195) | `0.6.5` |
| **`pygments`** | `2.19.1` | [`PYSEC-2026-2987`](https://osv.dev/vulnerability/PYSEC-2026-2987) | `2.20.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-1830`](https://osv.dev/vulnerability/PYSEC-2026-1830) | `6.0.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-1833`](https://osv.dev/vulnerability/PYSEC-2026-1833) | `6.1.3` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-1831`](https://osv.dev/vulnerability/PYSEC-2026-1831) | `6.1.3` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-1832`](https://osv.dev/vulnerability/PYSEC-2026-1832) | `6.4.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-1829`](https://osv.dev/vulnerability/PYSEC-2026-1829) | `6.6.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-1828`](https://osv.dev/vulnerability/PYSEC-2026-1828) | `6.6.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-1827`](https://osv.dev/vulnerability/PYSEC-2026-1827) | `6.6.2` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3015`](https://osv.dev/vulnerability/PYSEC-2026-3015) | `6.7.1` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3013`](https://osv.dev/vulnerability/PYSEC-2026-3013) | `6.7.1` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3024`](https://osv.dev/vulnerability/PYSEC-2026-3024) | `6.7.1` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3005`](https://osv.dev/vulnerability/PYSEC-2026-3005) | `6.7.2` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3027`](https://osv.dev/vulnerability/PYSEC-2026-3027) | `6.7.3` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3017`](https://osv.dev/vulnerability/PYSEC-2026-3017) | `6.7.4` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3014`](https://osv.dev/vulnerability/PYSEC-2026-3014) | `6.7.5` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3019`](https://osv.dev/vulnerability/PYSEC-2026-3019) | `6.8.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3023`](https://osv.dev/vulnerability/PYSEC-2026-3023) | `6.9.1` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3012`](https://osv.dev/vulnerability/PYSEC-2026-3012) | `6.9.2` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3006`](https://osv.dev/vulnerability/PYSEC-2026-3006) | `6.10.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3021`](https://osv.dev/vulnerability/PYSEC-2026-3021) | `6.10.1` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3007`](https://osv.dev/vulnerability/PYSEC-2026-3007) | `6.10.2` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3011`](https://osv.dev/vulnerability/PYSEC-2026-3011) | `6.10.2` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3026`](https://osv.dev/vulnerability/PYSEC-2026-3026) | `6.10.2` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3004`](https://osv.dev/vulnerability/PYSEC-2026-3004) | `6.12.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3016`](https://osv.dev/vulnerability/PYSEC-2026-3016) | `6.12.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3025`](https://osv.dev/vulnerability/PYSEC-2026-3025) | `6.12.1` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3020`](https://osv.dev/vulnerability/PYSEC-2026-3020) | `6.12.2` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3010`](https://osv.dev/vulnerability/PYSEC-2026-3010) | `6.12.2` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3022`](https://osv.dev/vulnerability/PYSEC-2026-3022) | `6.13.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3009`](https://osv.dev/vulnerability/PYSEC-2026-3009) | `6.13.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3018`](https://osv.dev/vulnerability/PYSEC-2026-3018) | `6.13.1` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3611`](https://osv.dev/vulnerability/PYSEC-2026-3611) | `6.14.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3610`](https://osv.dev/vulnerability/PYSEC-2026-3610) | `6.14.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3613`](https://osv.dev/vulnerability/PYSEC-2026-3613) | `6.14.2` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3612`](https://osv.dev/vulnerability/PYSEC-2026-3612) | `6.14.1` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3656`](https://osv.dev/vulnerability/PYSEC-2026-3656) | `6.15.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3655`](https://osv.dev/vulnerability/PYSEC-2026-3655) | `6.15.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3910`](https://osv.dev/vulnerability/PYSEC-2026-3910) | `6.16.1` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3912`](https://osv.dev/vulnerability/PYSEC-2026-3912) | `6.15.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3911`](https://osv.dev/vulnerability/PYSEC-2026-3911) | `6.16.1` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-3913`](https://osv.dev/vulnerability/PYSEC-2026-3913) | `6.16.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-4153`](https://osv.dev/vulnerability/PYSEC-2026-4153) | `6.18.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-4160`](https://osv.dev/vulnerability/PYSEC-2026-4160) | `6.19.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-4154`](https://osv.dev/vulnerability/PYSEC-2026-4154) | `6.18.1` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-4159`](https://osv.dev/vulnerability/PYSEC-2026-4159) | `6.19.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-4156`](https://osv.dev/vulnerability/PYSEC-2026-4156) | `6.18.1` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-4158`](https://osv.dev/vulnerability/PYSEC-2026-4158) | `6.17.0` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-4155`](https://osv.dev/vulnerability/PYSEC-2026-4155) | `6.18.1` |
| **`pypdf`** | `5.1.0` | [`PYSEC-2026-4157`](https://osv.dev/vulnerability/PYSEC-2026-4157) | `6.19.0` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-57204`](https://osv.dev/vulnerability/CVE-2026-57204) | `6.13.3` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-113792`](https://osv.dev/vulnerability/CVE-2026-113792) | `6.20.1` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-113795`](https://osv.dev/vulnerability/CVE-2026-113795) | `6.20.0` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-113793`](https://osv.dev/vulnerability/CVE-2026-113793) | `6.20.1` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-113794`](https://osv.dev/vulnerability/CVE-2026-113794) | `6.20.0` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-113786`](https://osv.dev/vulnerability/CVE-2026-113786) | `6.21.1` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-113791`](https://osv.dev/vulnerability/CVE-2026-113791) | `6.21.0` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-113790`](https://osv.dev/vulnerability/CVE-2026-113790) | `6.21.0` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-113789`](https://osv.dev/vulnerability/CVE-2026-113789) | `6.21.0` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-115572`](https://osv.dev/vulnerability/CVE-2026-115572) | `6.21.2` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-115585`](https://osv.dev/vulnerability/CVE-2026-115585) | `6.21.2` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-115580`](https://osv.dev/vulnerability/CVE-2026-115580) | `6.21.2` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-119208`](https://osv.dev/vulnerability/CVE-2026-119208) | `6.21.3` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-119206`](https://osv.dev/vulnerability/CVE-2026-119206) | `6.21.3` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-119209`](https://osv.dev/vulnerability/CVE-2026-119209) | `6.21.3` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-119207`](https://osv.dev/vulnerability/CVE-2026-119207) | `6.21.3` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-119203`](https://osv.dev/vulnerability/CVE-2026-119203) | `6.21.4` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-119205`](https://osv.dev/vulnerability/CVE-2026-119205) | `6.21.4` |
| **`pypdf`** | `5.1.0` | [`CVE-2026-119204`](https://osv.dev/vulnerability/CVE-2026-119204) | `6.21.4` |
| **`pypdf2`** | `3.0.1` | [`PYSEC-2026-1835`](https://osv.dev/vulnerability/PYSEC-2026-1835) | `3.9.0` |
| **`pytest`** | `8.3.4` | [`PYSEC-2026-1845`](https://osv.dev/vulnerability/PYSEC-2026-1845) | `9.0.3` |
| **`python-dotenv`** | `1.0.1` | [`PYSEC-2026-2270`](https://osv.dev/vulnerability/PYSEC-2026-2270) | `1.2.2` |
| **`requests`** | `2.32.3` | [`PYSEC-2026-1872`](https://osv.dev/vulnerability/PYSEC-2026-1872) | `2.32.4` |
| **`requests`** | `2.32.3` | [`PYSEC-2026-2275`](https://osv.dev/vulnerability/PYSEC-2026-2275) | `2.33.0` |
| **`setuptools`** | `79.0.1` | [`PYSEC-2026-3447`](https://osv.dev/vulnerability/PYSEC-2026-3447) | `83.0.0` |
| **`setuptools`** | `79.0.1` | [`GHSA-xmj3-9gf7-h52w`](https://osv.dev/vulnerability/GHSA-xmj3-9gf7-h52w) | `84.1.0` |
| **`soupsieve`** | `2.7` | [`PYSEC-2026-3072`](https://osv.dev/vulnerability/PYSEC-2026-3072) | `2.8.4` |
| **`soupsieve`** | `2.7` | [`PYSEC-2026-3071`](https://osv.dev/vulnerability/PYSEC-2026-3071) | `2.8.4` |
| **`soupsieve`** | `2.7` | [`PYSEC-2026-4170`](https://osv.dev/vulnerability/PYSEC-2026-4170) | `2.9.0` |
| **`soupsieve`** | `2.7` | [`PYSEC-2026-4171`](https://osv.dev/vulnerability/PYSEC-2026-4171) | `2.9.0` |
| **`sqlparse`** | `0.5.3` | [`PYSEC-2026-3697`](https://osv.dev/vulnerability/PYSEC-2026-3697) | `0.6.0` |
| **`sqlparse`** | `0.5.3` | [`PYSEC-2026-3696`](https://osv.dev/vulnerability/PYSEC-2026-3696) | `0.6.0` |
| **`sqlparse`** | `0.5.3` | [`PYSEC-2026-3698`](https://osv.dev/vulnerability/PYSEC-2026-3698) | `0.6.0` |
| **`sqlparse`** | `0.5.3` | [`PYSEC-2026-3699`](https://osv.dev/vulnerability/PYSEC-2026-3699) | `0.6.0` |
| **`sqlparse`** | `0.5.3` | [`PYSEC-2026-3923`](https://osv.dev/vulnerability/PYSEC-2026-3923) | `0.6.0` |
| **`sqlparse`** | `0.5.3` | [`GHSA-27jp-wm6q-gp25`](https://osv.dev/vulnerability/GHSA-27jp-wm6q-gp25) | `0.5.4` |
| **`streamlit`** | `1.46.1` | [`PYSEC-2026-2285`](https://osv.dev/vulnerability/PYSEC-2026-2285) | `1.54.0` |
| **`streamlit`** | `1.46.1` | [`PYSEC-2026-212`](https://osv.dev/vulnerability/PYSEC-2026-212) | `1.53.1` |
| **`torch`** | `2.7.0` | [`PYSEC-2026-1970`](https://osv.dev/vulnerability/PYSEC-2026-1970) | `2.8.0` |
| **`torch`** | `2.7.0` | [`PYSEC-2025-191`](https://osv.dev/vulnerability/PYSEC-2025-191) | `2.7.1rc1` |
| **`torch`** | `2.7.0` | [`PYSEC-2025-205`](https://osv.dev/vulnerability/PYSEC-2025-205) | `2.7.1` |
| **`torch`** | `2.7.0` | [`PYSEC-2025-206`](https://osv.dev/vulnerability/PYSEC-2025-206) | `2.9.0` |
| **`torch`** | `2.7.0` | [`PYSEC-2025-207`](https://osv.dev/vulnerability/PYSEC-2025-207) | `2.7.1` |
| **`torch`** | `2.7.0` | [`PYSEC-2025-204`](https://osv.dev/vulnerability/PYSEC-2025-204) | `2.9.0` |
| **`torch`** | `2.7.0` | [`PYSEC-2026-139`](https://osv.dev/vulnerability/PYSEC-2026-139) | `None specified` |
| **`torch`** | `2.7.0` | [`PYSEC-2025-209`](https://osv.dev/vulnerability/PYSEC-2025-209) | `2.7.1` |
| **`torch`** | `2.7.0` | [`PYSEC-2025-208`](https://osv.dev/vulnerability/PYSEC-2025-208) | `2.7.1` |
| **`torch`** | `2.7.0` | [`PYSEC-2025-203`](https://osv.dev/vulnerability/PYSEC-2025-203) | `2.9.0` |
| **`torch`** | `2.7.0` | [`PYSEC-2025-193`](https://osv.dev/vulnerability/PYSEC-2025-193) | `2.9.1` |
| **`torch`** | `2.7.0` | [`PYSEC-2025-194`](https://osv.dev/vulnerability/PYSEC-2025-194) | `2.13.0` |
| **`torch`** | `2.7.0` | [`PYSEC-2025-195`](https://osv.dev/vulnerability/PYSEC-2025-195) | `2.10.0` |
| **`torch`** | `2.7.0` | [`PYSEC-2026-2286`](https://osv.dev/vulnerability/PYSEC-2026-2286) | `2.10.0` |
| **`torch`** | `2.7.0` | [`PYSEC-2026-1856`](https://osv.dev/vulnerability/PYSEC-2026-1856) | `2.10.0` |
| **`tornado`** | `6.4.2` | [`PYSEC-2026-1974`](https://osv.dev/vulnerability/PYSEC-2026-1974) | `6.5` |
| **`tornado`** | `6.4.2` | [`PYSEC-2026-2287`](https://osv.dev/vulnerability/PYSEC-2026-2287) | `6.5.5` |
| **`tornado`** | `6.4.2` | [`PYSEC-2026-140`](https://osv.dev/vulnerability/PYSEC-2026-140) | `6.5.5` |
| **`tornado`** | `6.4.2` | [`PYSEC-2026-3388`](https://osv.dev/vulnerability/PYSEC-2026-3388) | `6.5.6` |
| **`tornado`** | `6.4.2` | [`PYSEC-2026-3387`](https://osv.dev/vulnerability/PYSEC-2026-3387) | `6.5.6` |
| **`tornado`** | `6.4.2` | [`PYSEC-2026-3389`](https://osv.dev/vulnerability/PYSEC-2026-3389) | `6.5.6` |
| **`tornado`** | `6.4.2` | [`PYSEC-2025-266`](https://osv.dev/vulnerability/PYSEC-2025-266) | `6.5.3` |
| **`tornado`** | `6.4.2` | [`PYSEC-2025-265`](https://osv.dev/vulnerability/PYSEC-2025-265) | `6.5.3` |
| **`tornado`** | `6.4.2` | [`PYSEC-2025-267`](https://osv.dev/vulnerability/PYSEC-2025-267) | `6.5.3` |
| **`tornado`** | `6.4.2` | [`PYSEC-2026-3928`](https://osv.dev/vulnerability/PYSEC-2026-3928) | `6.5.8` |
| **`tornado`** | `6.4.2` | [`GHSA-pw6j-qg29-8w7f`](https://osv.dev/vulnerability/GHSA-pw6j-qg29-8w7f) | `6.5.7` |
| **`tornado`** | `6.4.2` | [`GHSA-chx6-46f5-w4vp`](https://osv.dev/vulnerability/GHSA-chx6-46f5-w4vp) | `6.5.9` |
| **`tornado`** | `6.4.2` | [`GHSA-c2m8-h5v5-343r`](https://osv.dev/vulnerability/GHSA-c2m8-h5v5-343r) | `6.5.9` |
| **`tornado`** | `6.4.2` | [`GHSA-3hv7-mjh2-fv65`](https://osv.dev/vulnerability/GHSA-3hv7-mjh2-fv65) | `6.5.9` |
| **`tornado`** | `6.4.2` | [`GHSA-8423-8fgw-73vq`](https://osv.dev/vulnerability/GHSA-8423-8fgw-73vq) | `6.5.8` |
| **`tornado`** | `6.4.2` | [`CVE-2026-116577`](https://osv.dev/vulnerability/CVE-2026-116577) | `6.6` |
| **`tornado`** | `6.4.2` | [`CVE-2026-115927`](https://osv.dev/vulnerability/CVE-2026-115927) | `6.6` |
| **`tornado`** | `6.4.2` | [`CVE-2026-116578`](https://osv.dev/vulnerability/CVE-2026-116578) | `6.6` |
| **`transformers`** | `4.51.3` | [`PYSEC-2025-217`](https://osv.dev/vulnerability/PYSEC-2025-217) | `None specified` |
| **`transformers`** | `4.51.3` | [`PYSEC-2026-1986`](https://osv.dev/vulnerability/PYSEC-2026-1986) | `4.52.1` |
| **`transformers`** | `4.51.3` | [`PYSEC-2026-1977`](https://osv.dev/vulnerability/PYSEC-2026-1977) | `4.52.1` |
| **`transformers`** | `4.51.3` | [`PYSEC-2026-1983`](https://osv.dev/vulnerability/PYSEC-2026-1983) | `4.53.0` |
| **`transformers`** | `4.51.3` | [`PYSEC-2026-1981`](https://osv.dev/vulnerability/PYSEC-2026-1981) | `4.53.0` |
| **`transformers`** | `4.51.3` | [`PYSEC-2026-1988`](https://osv.dev/vulnerability/PYSEC-2026-1988) | `4.53.0` |
| **`transformers`** | `4.51.3` | [`PYSEC-2026-1980`](https://osv.dev/vulnerability/PYSEC-2026-1980) | `4.53.0` |
| **`transformers`** | `4.51.3` | [`PYSEC-2026-2288`](https://osv.dev/vulnerability/PYSEC-2026-2288) | `5.0.0rc3` |
| **`transformers`** | `4.51.3` | [`PYSEC-2025-214`](https://osv.dev/vulnerability/PYSEC-2025-214) | `None specified` |
| **`transformers`** | `4.51.3` | [`PYSEC-2025-218`](https://osv.dev/vulnerability/PYSEC-2025-218) | `None specified` |
| **`transformers`** | `4.51.3` | [`PYSEC-2025-211`](https://osv.dev/vulnerability/PYSEC-2025-211) | `None specified` |
| **`transformers`** | `4.51.3` | [`PYSEC-2025-212`](https://osv.dev/vulnerability/PYSEC-2025-212) | `None specified` |
| **`transformers`** | `4.51.3` | [`PYSEC-2025-213`](https://osv.dev/vulnerability/PYSEC-2025-213) | `None specified` |
| **`transformers`** | `4.51.3` | [`PYSEC-2025-215`](https://osv.dev/vulnerability/PYSEC-2025-215) | `None specified` |
| **`transformers`** | `4.51.3` | [`PYSEC-2025-216`](https://osv.dev/vulnerability/PYSEC-2025-216) | `None specified` |
| **`transformers`** | `4.51.3` | [`PYSEC-2026-2289`](https://osv.dev/vulnerability/PYSEC-2026-2289) | `5.3.0` |
| **`transformers`** | `4.51.3` | [`PYSEC-2026-2290`](https://osv.dev/vulnerability/PYSEC-2026-2290) | `None specified` |
| **`transformers`** | `4.51.3` | [`PYSEC-2026-3929`](https://osv.dev/vulnerability/PYSEC-2026-3929) | `5.10.0` |
| **`transformers`** | `4.51.3` | [`PYSEC-2026-4174`](https://osv.dev/vulnerability/PYSEC-2026-4174) | `None specified` |
| **`urllib3`** | `2.5.0` | [`PYSEC-2026-1998`](https://osv.dev/vulnerability/PYSEC-2026-1998) | `2.6.0` |
| **`urllib3`** | `2.5.0` | [`PYSEC-2026-1994`](https://osv.dev/vulnerability/PYSEC-2026-1994) | `2.6.0` |
| **`urllib3`** | `2.5.0` | [`PYSEC-2026-1996`](https://osv.dev/vulnerability/PYSEC-2026-1996) | `2.6.3` |
| **`urllib3`** | `2.5.0` | [`PYSEC-2026-141`](https://osv.dev/vulnerability/PYSEC-2026-141) | `2.7.0` |
| **`urllib3`** | `2.5.0` | [`PYSEC-2026-4177`](https://osv.dev/vulnerability/PYSEC-2026-4177) | `2.8.0` |
| **`urllib3`** | `2.5.0` | [`PYSEC-2026-4175`](https://osv.dev/vulnerability/PYSEC-2026-4175) | `2.8.0` |
| **`virtualenv`** | `20.30.0` | [`PYSEC-2026-2009`](https://osv.dev/vulnerability/PYSEC-2026-2009) | `20.36.1` |
| **`virtualenv`** | `20.30.0` | [`PYSEC-2026-4011`](https://osv.dev/vulnerability/PYSEC-2026-4011) | `21.7.12` |
| **`virtualenv`** | `20.30.0` | [`PYSEC-2026-4012`](https://osv.dev/vulnerability/PYSEC-2026-4012) | `21.7.11` |
| **`virtualenv`** | `20.30.0` | [`PYSEC-2026-4014`](https://osv.dev/vulnerability/PYSEC-2026-4014) | `21.7.12` |
| **`virtualenv`** | `20.30.0` | [`PYSEC-2026-4013`](https://osv.dev/vulnerability/PYSEC-2026-4013) | `21.7.13` |
| **`virtualenv`** | `20.30.0` | [`CVE-2026-113732`](https://osv.dev/vulnerability/CVE-2026-113732) | `21.14.2` |
| **`virtualenv`** | `20.30.0` | [`CVE-2026-113726`](https://osv.dev/vulnerability/CVE-2026-113726) | `21.14.4` |
| **`virtualenv`** | `20.30.0` | [`CVE-2026-113776`](https://osv.dev/vulnerability/CVE-2026-113776) | `21.14.2` |
| **`virtualenv`** | `20.30.0` | [`CVE-2026-113725`](https://osv.dev/vulnerability/CVE-2026-113725) | `21.14.7` |
| **`virtualenv`** | `20.30.0` | [`CVE-2026-113722`](https://osv.dev/vulnerability/CVE-2026-113722) | `21.14.9` |
| **`virtualenv`** | `20.30.0` | [`CVE-2026-113714`](https://osv.dev/vulnerability/CVE-2026-113714) | `21.14.9` |
| **`virtualenv`** | `20.30.0` | [`CVE-2026-113723`](https://osv.dev/vulnerability/CVE-2026-113723) | `21.14.9` |
| **`virtualenv`** | `20.30.0` | [`CVE-2026-113715`](https://osv.dev/vulnerability/CVE-2026-113715) | `21.14.9` |
| **`virtualenv`** | `20.30.0` | [`CVE-2026-113720`](https://osv.dev/vulnerability/CVE-2026-113720) | `21.14.9` |
| **`virtualenv`** | `20.30.0` | [`CVE-2026-113717`](https://osv.dev/vulnerability/CVE-2026-113717) | `21.14.9` |
| **`virtualenv`** | `20.30.0` | [`CVE-2026-113718`](https://osv.dev/vulnerability/CVE-2026-113718) | `21.14.9` |
| **`weasyprint`** | `68.1` | [`PYSEC-2026-3412`](https://osv.dev/vulnerability/PYSEC-2026-3412) | `None specified` |
| **`weasyprint`** | `68.1` | [`PYSEC-2026-3940`](https://osv.dev/vulnerability/PYSEC-2026-3940) | `70.0` |
| **`weasyprint`** | `68.1` | [`PYSEC-2026-4311`](https://osv.dev/vulnerability/PYSEC-2026-4311) | `70.0` |
| **`werkzeug`** | `3.1.3` | [`PYSEC-2026-2046`](https://osv.dev/vulnerability/PYSEC-2026-2046) | `3.1.4` |
| **`werkzeug`** | `3.1.3` | [`PYSEC-2026-2044`](https://osv.dev/vulnerability/PYSEC-2026-2044) | `3.1.5` |
| **`werkzeug`** | `3.1.3` | [`PYSEC-2026-2320`](https://osv.dev/vulnerability/PYSEC-2026-2320) | `3.1.6` |
| **`werkzeug`** | `3.1.3` | [`PYSEC-2026-4312`](https://osv.dev/vulnerability/PYSEC-2026-4312) | `3.1.9` |

## 🛠️ Security Remediation Guidance

- [ ] **Rotate / Environment Variables**: Ensure all database URLs, API tokens, and JWT secrets are injected via `.env` or GitHub Secrets, never hardcoded in source.
- [ ] **Parameterized Queries**: Verify that SQL queries in `app.py` use SQLAlchemy ORM or bound parameters (`db.session.execute(text(...), {'param': val})`).
- [ ] **Dependency Patching**: Run `pip install --upgrade <package>` to bump flagged libraries to their recommended patch versions.
- [ ] **CSRF & Session Hardening**: Ensure `WTF_CSRF_ENABLED=True` and secure cookie flags (`SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`) are active.

---
*This report is automatically generated and updated on each push and scheduled audit by the AI JobSnap Security Agent workflow.*
