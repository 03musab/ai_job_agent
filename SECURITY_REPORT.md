# 🛡️ Automated Security Audit Report

> **Status:** 🔴 **Action Required**  
> **Generated:** `2026-11-13 08:56:38 UTC`  
> **Branch/Ref:** `main` (`cfdd1d1b`)  

## 📊 Executive Summary

| Category | Findings | Severity Note |
| :--- | :--- | :--- |
| **🚨 High Severity (Code)** | `9` | Critical flaws, injection, or hardcoded secrets |
| **⚠️ Medium Severity (Code)** | `12` | Weak crypto, insecure configs, or unvalidated parameters |
| **ℹ️ Low Severity (Code)** | `39` | Information leaks or minor code hygiene warnings |
| **📦 Known CVEs (Dependencies)** | `0` | Vulnerabilities identified in third-party packages |
| **Total Security Items** | `60` | Combined code & dependency signals |

## 🔍 Code Security Vulnerabilities (SAST)

Identified `60` code security items across Python source files:

### 1. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:1219`](./app.py#L1219)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
1218         norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}|{user_id}"
1219         job_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
1220
```

### 2. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:1958`](./app.py#L1958)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
1957                 norm = f"{normalize_for_hash(title)}|{normalize_for_hash(company)}|{normalize_for_hash(location)}|{user_id}"
1958                 new_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
1959                 if new_hash != old_hash:
```

### 3. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:3985`](./app.py#L3985)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
3984             norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}"
3985             key = hashlib.md5(norm.encode('utf-8')).hexdigest()
3986             if key not in unique_jobs or job.relevance_score > unique_jobs[key].relevance_score:
```

### 4. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:6824`](./app.py#L6824)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
6823                     if not processed_row.get('linkedin_url') and processed_row.get('email'):
6824                         email_hash = hashlib.md5(str(processed_row['email']).lower().encode()).hexdigest()
6825                         processed_row['linkedin_url'] = f"csv-upload-{email_hash}"
```

### 5. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:7121`](./app.py#L7121)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
7120                             if contact_data.get('email'):
7121                                 email_hash = hashlib.md5(contact_data['email'].lower().encode()).hexdigest()
7122                                 contact_data['linkedin_url'] = f"repo-{email_hash}"
```

### 6. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:7125`](./app.py#L7125)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
7124                                 unique_str = f"{contact_data.get('full_name')}-{contact_data.get('company')}"
7125                                 unique_hash = hashlib.md5(unique_str.encode()).hexdigest()
7126                                 contact_data['linkedin_url'] = f"repo-noemail-{unique_hash}"
```

### 7. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:7237`](./app.py#L7237)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
7236     if not linkedin_url:
7237         email_hash = hashlib.md5(data['email'].lower().encode()).hexdigest()
7238         linkedin_url = f"manual-entry-{email_hash}"
```

### 8. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:7310`](./app.py#L7310)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
7309                 if not processed_row.get('linkedin_url') and processed_row.get('email'):
7310                     email_hash = hashlib.md5(processed_row['email'].lower().encode()).hexdigest()
7311                     processed_row['linkedin_url'] = f"csv-import-{email_hash}"
```

### 9. [🚨 HIGH] A Flask app appears to be run with debug=True, which exposes the Werkzeug debugger and allows the execution of arbitrary code.
- **File:** [`./app.py:9549`](./app.py#L9549)
- **Rule ID:** `B201` (flask_debug_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b201_flask_debug_true.html)

```python
9548         logger.warning(f"Could not automatically open browser: {e}")
9549     app.run(debug=True, host='0.0.0.0', port=5000)
```

### 10. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1309`](./app.py#L1309)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1308         """
1309         query = f"SELECT {query_columns} FROM jobs WHERE (user_id = ? OR user_id = 15 OR user_id IS NULL OR posted_by_recruiter_id IS NOT NULL)"
1310         params = [user_id]
```

### 11. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1365`](./app.py#L1365)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1364 
1365         count_query = f"SELECT COUNT(*) FROM ({query})"
1366         cursor.execute(count_query, params)
```

### 12. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1554`](./app.py#L1554)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1553             placeholders = ','.join(['?'] * len(job_ids))
1554             cursor.execute(f"DELETE FROM jobs WHERE id IN ({placeholders}) AND user_id = ?", (*job_ids, user_id))
1555             deleted_count = cursor.rowcount
```

### 13. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:2925`](./app.py#L2925)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
2924 
2925         search_query = f"SELECT * FROM global_hiring_contacts WHERE {' OR '.join(where_clauses)}"
2926         cursor.execute(search_query, params)
```

### 14. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:4406`](./app.py#L4406)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
4405             with open('token.pickle', 'rb') as token:
4406                 creds = pickle.load(token)
4407
```

### 15. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:4892`](./app.py#L4892)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
4891             with open('token.pickle', 'rb') as token:
4892                 creds = pickle.load(token)
4893
```

### 16. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:5896`](./app.py#L5896)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
5895     with open(token_path, 'rb') as token_file:
5896         creds = pickle.load(token_file)
5897
```

### 17. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./app.py:9549`](./app.py#L9549)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
9548         logger.warning(f"Could not automatically open browser: {e}")
9549     app.run(debug=True, host='0.0.0.0', port=5000)
```

### 18. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./database.py:62`](./database.py#L62)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
61         return (
62             "SELECT ordinal_position - 1 AS cid, column_name AS name "
63             "FROM information_schema.columns "
64             "WHERE table_schema = current_schema() AND table_name = "
65             f"'{table_name}' ORDER BY ordinal_position"
66         )
```

### 19. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./scripts/migrate_sqlite_to_postgres.py:116`](./scripts/migrate_sqlite_to_postgres.py#L116)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
115     )
116     source_cursor = source.execute(f'SELECT * FROM "{table}"')
117     copied = 0
```

### 20. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./scripts/proc_runner.py:120`](./scripts/proc_runner.py#L120)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
119     debug = _is_truthy(os.environ.get("FLASK_DEBUG") or os.environ.get("DEBUG"))
120     app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
121     return 0
```

### 21. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./send_launch_emails.py:163`](./send_launch_emails.py#L163)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
162     with open(token_path, "rb") as token:
163         creds = pickle.load(token)
164
```

### 22. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:23`](./ai_utils.py#L23)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
22         return json.loads(text)
23     except Exception:
24         pass
25
```

### 23. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./ai_utils.py:37`](./ai_utils.py#L37)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
36             return json.loads(cand)
37         except Exception:
38             continue
39
```

### 24. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:47`](./ai_utils.py#L47)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
46             return json.loads(sub)
47         except Exception:
48             pass
49
```

### 25. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:57`](./ai_utils.py#L57)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
56             return json.loads(sub)
57         except Exception:
58             pass
59
```

### 26. [ℹ️ LOW] Consider possible security implications associated with pickle module.
- **File:** [`./app.py:12`](./app.py#L12)
- **Rule ID:** `B403` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b403-import-pickle)

```python
11 import os
12 import pickle
13 import random
```

### 27. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:2234`](./app.py#L2234)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
2233                     date_counts[dt_part] = date_counts.get(dt_part, 0) + 1
2234                 except Exception:
2235                     continue
2236
```

### 28. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2791`](./app.py#L2791)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2790                         ''', (user_id, dt['template_name'], dt['subject'], dt['body'], now_str))
2791                     except Exception:
2792                         pass
2793                 conn.commit()
```

### 29. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2983`](./app.py#L2983)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2982                         ))
2983                     except Exception:
2984                         pass
2985                 conn.commit()
```

### 30. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3123`](./app.py#L3123)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3122             options.add_argument('--disable-dev-shm-usage')
3123             random_user_agent = random.choice(USER_AGENTS)
3124             options.add_argument(f"user-agent={random_user_agent}")
```

### 31. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3345`](./app.py#L3345)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3344             }
3345             headers = {'User-Agent': random.choice(USER_AGENTS)}
3346             try:
```

### 32. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3348`](./app.py#L3348)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3347                 logger.info(f"[LinkedIn] Sending request to LinkedIn for job list (page {page + 1})...")
3348                 time.sleep(random.uniform(*self.request_delay))  # Dynamic delay based on scan mode
3349                 response = requests.get(base_url, params=params, headers=headers, timeout=15, proxies=proxies)
```

### 33. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3416`](./app.py#L3416)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3415                         logger.info(f"[LinkedIn] Fetching job detail page: {job['link']}")
3416                         detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
3417                         time.sleep(random.uniform(2.5, 5.5)) # Increased delay to avoid 429 errors
```

### 34. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3417`](./app.py#L3417)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3416                         detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
3417                         time.sleep(random.uniform(2.5, 5.5)) # Increased delay to avoid 429 errors
3418                         resp = requests.get(job['link'], headers=detail_headers, timeout=15)
```

### 35. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3494`](./app.py#L3494)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3493             session.headers.update({
3494                 'User-Agent': random.choice(USER_AGENTS),
3495                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
```

### 36. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3516`](./app.py#L3516)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3515                     # Randomized delay to avoid detection
3516                     time.sleep(random.uniform(*self.request_delay))
3517
```

### 37. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3716`](./app.py#L3716)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3715             # Randomized delay
3716             time.sleep(random.uniform(1.5, 3.5))
3717
```

### 38. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3719`](./app.py#L3719)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3718             headers = {
3719                 'User-Agent': random.choice(USER_AGENTS),
3720                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
```

### 39. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:4992`](./app.py#L4992)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
4991                                 row[rel_col-1].value = f"🔴 {val}"
4992                         except:
4993                             continue
4994                 # --- Make Links Clickable and Button Style ---
```

### 40. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:5574`](./app.py#L5574)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
5573                 logger.info(f"Cleaned up Excel report: {excel_file}.")
5574             except Exception:
5575                 pass
5576
```

### 41. [ℹ️ LOW] Possible hardcoded password: 'token.pickle'
- **File:** [`./app.py:5891`](./app.py#L5891)
- **Rule ID:** `B105` (hardcoded_password_string)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b105_hardcoded_password_string.html)

```python
5890     """Send a MIME message via existing non-interactive Gmail OAuth credentials."""
5891     token_path = 'token.pickle'
5892     if not os.path.exists(token_path):
```

### 42. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:6499`](./app.py#L6499)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
6498                         experience_summary = f"experience as {role}" + (f" at {comp}" if comp else "")
6499             except Exception:
6500                 pass
6501
```

### 43. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:7621`](./app.py#L7621)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
7620         conn.close()
7621     except Exception as e:
7622         pass
7623
```

### 44. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:7987`](./app.py#L7987)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
7986     fake_analysis_data = {
7987         "monthly_visits": f"{random.randint(50, 500)}K",
7988         "bounce_rate": f"{random.randint(30, 70)}%",
```

### 45. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:7988`](./app.py#L7988)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
7987         "monthly_visits": f"{random.randint(50, 500)}K",
7988         "bounce_rate": f"{random.randint(30, 70)}%",
7989         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
```

### 46. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:7989`](./app.py#L7989)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
7988         "bounce_rate": f"{random.randint(30, 70)}%",
7989         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
7990     }
```

### 47. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:8515`](./app.py#L8515)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
8514                 db.update_job_status_and_notes(job_id, current_user.id, 'applied', notes or 'Applied directly via JobSnap')
8515             except Exception:
8516                 pass
8517             return jsonify({
```

### 48. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:9469`](./app.py#L9469)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
9468                 user_name = user_details.get('full_name')
9469         except: pass
9470
```

### 49. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./outreach_scraper.py:48`](./outreach_scraper.py#L48)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
47         self.session = requests.Session()
48         self.session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
49         self.scraped_domains = set()
```

### 50. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./outreach_scraper.py:108`](./outreach_scraper.py#L108)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
107         # Add random delay to appear more human
108         time.sleep(random.uniform(self.min_delay, self.max_delay))
109
```

### 51. [ℹ️ LOW] Consider possible security implications associated with the subprocess module.
- **File:** [`./scripts/proc_runner.py:14`](./scripts/proc_runner.py#L14)
- **Rule ID:** `B404` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess)

```python
13 import os
14 import subprocess
15 import sys
```

### 52. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:293`](./scripts/proc_runner.py#L293)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
292             sys.stderr.flush()
293         except Exception:
294             pass
295         if job_handle:
```

### 53. [ℹ️ LOW] Starting a process with a partial executable path
- **File:** [`./scripts/proc_runner.py:299`](./scripts/proc_runner.py#L299)
- **Rule ID:** `B607` (start_process_with_partial_path)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b607_start_process_with_partial_path.html)

```python
298             try:
299                 subprocess.run(
300                     ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
301                     stdout=subprocess.DEVNULL,
302                     stderr=subprocess.DEVNULL,
303                     timeout=3,
304                     check=False,
305                 )
306             except Exception:
```

### 54. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./scripts/proc_runner.py:299`](./scripts/proc_runner.py#L299)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
298             try:
299                 subprocess.run(
300                     ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
301                     stdout=subprocess.DEVNULL,
302                     stderr=subprocess.DEVNULL,
303                     timeout=3,
304                     check=False,
305                 )
306             except Exception:
```

### 55. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:306`](./scripts/proc_runner.py#L306)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
305                 )
306             except Exception:
307                 pass
308             try:
```

### 56. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:310`](./scripts/proc_runner.py#L310)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
309                 proc.kill()
310             except Exception:
311                 pass
312         os._exit(0)
```

### 57. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./scripts/proc_runner.py:332`](./scripts/proc_runner.py#L332)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
331 
332         proc = subprocess.Popen(cmd, env=env, cwd=str(REPO_ROOT))
333         if child_job is not None:
```

### 58. [ℹ️ LOW] Starting a process without a shell.
- **File:** [`./scripts/proc_runner.py:398`](./scripts/proc_runner.py#L398)
- **Rule ID:** `B606` (start_process_with_no_shell)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b606_start_process_with_no_shell.html)

```python
397         os.chdir(REPO_ROOT)
398         os.execvpe(cmd[0], cmd, env)
399
```

### 59. [ℹ️ LOW] Consider possible security implications associated with pickle module.
- **File:** [`./send_launch_emails.py:12`](./send_launch_emails.py#L12)
- **Rule ID:** `B403` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b403-import-pickle)

```python
11 import base64
12 import pickle
13 import argparse
```

### 60. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
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
