# 🛡️ Automated Security Audit Report

> **Status:** 🔴 **Action Required**  
> **Generated:** `2026-11-08 08:24:37 UTC`  
> **Branch/Ref:** `main` (`f9413cbd`)  

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
- **File:** [`./app.py:1130`](./app.py#L1130)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
1129         norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}|{user_id}"
1130         job_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
1131
```

### 2. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:1863`](./app.py#L1863)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
1862                 norm = f"{normalize_for_hash(title)}|{normalize_for_hash(company)}|{normalize_for_hash(location)}|{user_id}"
1863                 new_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
1864                 if new_hash != old_hash:
```

### 3. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:3874`](./app.py#L3874)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
3873             norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}"
3874             key = hashlib.md5(norm.encode('utf-8')).hexdigest()
3875             if key not in unique_jobs or job.relevance_score > unique_jobs[key].relevance_score:
```

### 4. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6179`](./app.py#L6179)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6178                     if not processed_row.get('linkedin_url') and processed_row.get('email'):
6179                         email_hash = hashlib.md5(str(processed_row['email']).lower().encode()).hexdigest()
6180                         processed_row['linkedin_url'] = f"csv-upload-{email_hash}"
```

### 5. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6477`](./app.py#L6477)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6476                             if contact_data.get('email'):
6477                                 email_hash = hashlib.md5(contact_data['email'].lower().encode()).hexdigest()
6478                                 contact_data['linkedin_url'] = f"repo-{email_hash}"
```

### 6. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6481`](./app.py#L6481)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6480                                 unique_str = f"{contact_data.get('full_name')}-{contact_data.get('company')}"
6481                                 unique_hash = hashlib.md5(unique_str.encode()).hexdigest()
6482                                 contact_data['linkedin_url'] = f"repo-noemail-{unique_hash}"
```

### 7. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6593`](./app.py#L6593)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6592     if not linkedin_url:
6593         email_hash = hashlib.md5(data['email'].lower().encode()).hexdigest()
6594         linkedin_url = f"manual-entry-{email_hash}"
```

### 8. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6666`](./app.py#L6666)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6665                 if not processed_row.get('linkedin_url') and processed_row.get('email'):
6666                     email_hash = hashlib.md5(processed_row['email'].lower().encode()).hexdigest()
6667                     processed_row['linkedin_url'] = f"csv-import-{email_hash}"
```

### 9. [🚨 HIGH] A Flask app appears to be run with debug=True, which exposes the Werkzeug debugger and allows the execution of arbitrary code.
- **File:** [`./app.py:8905`](./app.py#L8905)
- **Rule ID:** `B201` (flask_debug_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b201_flask_debug_true.html)

```python
8904         logger.warning(f"Could not automatically open browser: {e}")
8905     app.run(debug=True, host='0.0.0.0', port=5000)
```

### 10. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1220`](./app.py#L1220)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1219         """
1220         query = f"SELECT {query_columns} FROM jobs WHERE (user_id = ? OR user_id = 15 OR user_id IS NULL OR posted_by_recruiter_id IS NOT NULL)"
1221         params = [user_id]
```

### 11. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1276`](./app.py#L1276)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1275 
1276         count_query = f"SELECT COUNT(*) FROM ({query})"
1277         cursor.execute(count_query, params)
```

### 12. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1459`](./app.py#L1459)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1458             placeholders = ','.join(['?'] * len(job_ids))
1459             cursor.execute(f"DELETE FROM jobs WHERE id IN ({placeholders}) AND user_id = ?", (*job_ids, user_id))
1460             deleted_count = cursor.rowcount
```

### 13. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:2814`](./app.py#L2814)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
2813 
2814         search_query = f"SELECT * FROM global_hiring_contacts WHERE {' OR '.join(where_clauses)}"
2815         cursor.execute(search_query, params)
```

### 14. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:4295`](./app.py#L4295)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
4294             with open('token.pickle', 'rb') as token:
4295                 creds = pickle.load(token)
4296
```

### 15. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:4781`](./app.py#L4781)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
4780             with open('token.pickle', 'rb') as token:
4781                 creds = pickle.load(token)
4782
```

### 16. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./app.py:8905`](./app.py#L8905)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
8904         logger.warning(f"Could not automatically open browser: {e}")
8905     app.run(debug=True, host='0.0.0.0', port=5000)
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
- **File:** [`./app.py:2123`](./app.py#L2123)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
2122                     date_counts[dt_part] = date_counts.get(dt_part, 0) + 1
2123                 except Exception:
2124                     continue
2125
```

### 24. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2680`](./app.py#L2680)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2679                         ''', (user_id, dt['template_name'], dt['subject'], dt['body'], now_str))
2680                     except Exception:
2681                         pass
2682                 conn.commit()
```

### 25. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2872`](./app.py#L2872)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2871                         ))
2872                     except Exception:
2873                         pass
2874                 conn.commit()
```

### 26. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3012`](./app.py#L3012)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3011             options.add_argument('--disable-dev-shm-usage')
3012             random_user_agent = random.choice(USER_AGENTS)
3013             options.add_argument(f"user-agent={random_user_agent}")
```

### 27. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3234`](./app.py#L3234)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3233             }
3234             headers = {'User-Agent': random.choice(USER_AGENTS)}
3235             try:
```

### 28. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3237`](./app.py#L3237)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3236                 logger.info(f"[LinkedIn] Sending request to LinkedIn for job list (page {page + 1})...")
3237                 time.sleep(random.uniform(*self.request_delay))  # Dynamic delay based on scan mode
3238                 response = requests.get(base_url, params=params, headers=headers, timeout=15, proxies=proxies)
```

### 29. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3305`](./app.py#L3305)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3304                         logger.info(f"[LinkedIn] Fetching job detail page: {job['link']}")
3305                         detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
3306                         time.sleep(random.uniform(2.5, 5.5)) # Increased delay to avoid 429 errors
```

### 30. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3306`](./app.py#L3306)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3305                         detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
3306                         time.sleep(random.uniform(2.5, 5.5)) # Increased delay to avoid 429 errors
3307                         resp = requests.get(job['link'], headers=detail_headers, timeout=15)
```

### 31. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3383`](./app.py#L3383)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3382             session.headers.update({
3383                 'User-Agent': random.choice(USER_AGENTS),
3384                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
```

### 32. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3405`](./app.py#L3405)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3404                     # Randomized delay to avoid detection
3405                     time.sleep(random.uniform(*self.request_delay))
3406
```

### 33. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3605`](./app.py#L3605)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3604             # Randomized delay
3605             time.sleep(random.uniform(1.5, 3.5))
3606
```

### 34. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3608`](./app.py#L3608)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3607             headers = {
3608                 'User-Agent': random.choice(USER_AGENTS),
3609                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
```

### 35. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:4881`](./app.py#L4881)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
4880                                 row[rel_col-1].value = f"🔴 {val}"
4881                         except:
4882                             continue
4883                 # --- Make Links Clickable and Button Style ---
```

### 36. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:5463`](./app.py#L5463)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
5462                 logger.info(f"Cleaned up Excel report: {excel_file}.")
5463             except Exception:
5464                 pass
5465
```

### 37. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:5844`](./app.py#L5844)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
5843                         experience_summary = f"experience as {role}" + (f" at {comp}" if comp else "")
5844             except Exception:
5845                 pass
5846
```

### 38. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:6977`](./app.py#L6977)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
6976         conn.close()
6977     except Exception as e:
6978         pass
6979
```

### 39. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:7343`](./app.py#L7343)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
7342     fake_analysis_data = {
7343         "monthly_visits": f"{random.randint(50, 500)}K",
7344         "bounce_rate": f"{random.randint(30, 70)}%",
```

### 40. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:7344`](./app.py#L7344)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
7343         "monthly_visits": f"{random.randint(50, 500)}K",
7344         "bounce_rate": f"{random.randint(30, 70)}%",
7345         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
```

### 41. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:7345`](./app.py#L7345)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
7344         "bounce_rate": f"{random.randint(30, 70)}%",
7345         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
7346     }
```

### 42. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:7871`](./app.py#L7871)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
7870                 db.update_job_status_and_notes(job_id, current_user.id, 'applied', notes or 'Applied directly via JobSnap')
7871             except Exception:
7872                 pass
7873             return jsonify({
```

### 43. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:8825`](./app.py#L8825)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
8824                 user_name = user_details.get('full_name')
8825         except: pass
8826
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
