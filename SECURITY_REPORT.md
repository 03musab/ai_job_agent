# 🛡️ Automated Security Audit Report

> **Status:** 🔴 **Action Required**  
> **Generated:** `2026-11-16 08:51:11 UTC`  
> **Branch/Ref:** `main` (`a148007b`)  

## 📊 Executive Summary

| Category | Findings | Severity Note |
| :--- | :--- | :--- |
| **🚨 High Severity (Code)** | `8` | Critical flaws, injection, or hardcoded secrets |
| **⚠️ Medium Severity (Code)** | `15` | Weak crypto, insecure configs, or unvalidated parameters |
| **ℹ️ Low Severity (Code)** | `40` | Information leaks or minor code hygiene warnings |
| **📦 Known CVEs (Dependencies)** | `0` | Vulnerabilities identified in third-party packages |
| **Total Security Items** | `63` | Combined code & dependency signals |

## 🔍 Code Security Vulnerabilities (SAST)

Identified `63` code security items across Python source files:

### 1. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:1409`](./app.py#L1409)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
1408         norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}|{user_id}"
1409         job_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
1410
```

### 2. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:2162`](./app.py#L2162)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
2161                 norm = f"{normalize_for_hash(title)}|{normalize_for_hash(company)}|{normalize_for_hash(location)}|{user_id}"
2162                 new_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
2163                 if new_hash != old_hash:
```

### 3. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:4189`](./app.py#L4189)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
4188             norm = f"{normalize_for_hash(job.title)}|{normalize_for_hash(job.company)}|{normalize_for_hash(job.location)}"
4189             key = hashlib.md5(norm.encode('utf-8')).hexdigest()
4190             if key not in unique_jobs or job.relevance_score > unique_jobs[key].relevance_score:
```

### 4. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:7698`](./app.py#L7698)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
7697                     if not processed_row.get('linkedin_url') and processed_row.get('email'):
7698                         email_hash = hashlib.md5(str(processed_row['email']).lower().encode()).hexdigest()
7699                         processed_row['linkedin_url'] = f"csv-upload-{email_hash}"
```

### 5. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:7995`](./app.py#L7995)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
7994                             if contact_data.get('email'):
7995                                 email_hash = hashlib.md5(contact_data['email'].lower().encode()).hexdigest()
7996                                 contact_data['linkedin_url'] = f"repo-{email_hash}"
```

### 6. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:7999`](./app.py#L7999)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
7998                                 unique_str = f"{contact_data.get('full_name')}-{contact_data.get('company')}"
7999                                 unique_hash = hashlib.md5(unique_str.encode()).hexdigest()
8000                                 contact_data['linkedin_url'] = f"repo-noemail-{unique_hash}"
```

### 7. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:8115`](./app.py#L8115)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
8114     if not linkedin_url:
8115         email_hash = hashlib.md5(data['email'].lower().encode()).hexdigest()
8116         linkedin_url = f"manual-entry-{email_hash}"
```

### 8. [🚨 HIGH] Use of weak MD5 hash for security. Consider usedforsecurity=False
- **File:** [`./app.py:8188`](./app.py#L8188)
- **Rule ID:** `B324` (hashlib)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b324_hashlib.html)

```python
8187                 if not processed_row.get('linkedin_url') and processed_row.get('email'):
8188                     email_hash = hashlib.md5(processed_row['email'].lower().encode()).hexdigest()
8189                     processed_row['linkedin_url'] = f"csv-import-{email_hash}"
```

### 9. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1511`](./app.py#L1511)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1510         scope_clause = self._user_scope_clause(cursor, user_id)
1511         query = f"SELECT {query_columns} FROM jobs WHERE {scope_clause}"
1512         params = [user_id]
```

### 10. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1567`](./app.py#L1567)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1566 
1567         count_query = f"SELECT COUNT(*) FROM ({query}) AS filtered_jobs_count"
1568         cursor.execute(count_query, params)
```

### 11. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1756`](./app.py#L1756)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1755             placeholders = ','.join(['?'] * len(job_ids))
1756             cursor.execute(f"DELETE FROM jobs WHERE id IN ({placeholders}) AND user_id = ?", (*job_ids, user_id))
1757             deleted_count = cursor.rowcount
```

### 12. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:1798`](./app.py#L1798)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
1797             scope_clause = self._user_scope_clause(cursor, user_id)
1798             cursor.execute(f"SELECT status, COUNT(*) FROM jobs WHERE {scope_clause} AND status IS NOT NULL GROUP BY status", (user_id,))
1799             rows = cursor.fetchall()
```

### 13. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:2039`](./app.py#L2039)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
2038             scope_clause = self._user_scope_clause(cursor, user_id)
2039             cursor.execute(f"""
2040                 SELECT * FROM jobs WHERE {scope_clause}
2041                 ORDER BY found_date DESC
2042             """, (user_id,))
2043             all_jobs = [dict(r) for r in cursor.fetchall()]
```

### 14. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./app.py:3129`](./app.py#L3129)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
3128 
3129         search_query = f"SELECT * FROM global_hiring_contacts WHERE {' OR '.join(where_clauses)}"
3130         cursor.execute(search_query, params)
```

### 15. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:4610`](./app.py#L4610)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
4609             with open('token.pickle', 'rb') as token:
4610                 creds = pickle.load(token)
4611
```

### 16. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:5096`](./app.py#L5096)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
5095             with open('token.pickle', 'rb') as token:
5096                 creds = pickle.load(token)
5097
```

### 17. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./app.py:6112`](./app.py#L6112)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
6111     with open(token_path, 'rb') as token_file:
6112         creds = pickle.load(token_file)
6113
```

### 18. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./app.py:6805`](./app.py#L6805)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
6804         return False
6805     return hostname.strip().lower() in ('localhost', '127.0.0.1', '0.0.0.0', '::1')
6806
```

### 19. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./app.py:10439`](./app.py#L10439)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
10438     logger.info(f"Starting Flask application on 0.0.0.0:{port} (debug={debug_mode})...")
10439     app.run(debug=debug_mode, host='0.0.0.0', port=port)
```

### 20. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./database.py:71`](./database.py#L71)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
70         return (
71             "SELECT ordinal_position - 1 AS cid, column_name AS name "
72             "FROM information_schema.columns "
73             "WHERE table_schema = current_schema() AND table_name = "
74             f"'{table_name}' ORDER BY ordinal_position"
75         )
```

### 21. [⚠️ MEDIUM] Possible SQL injection vector through string-based query construction.
- **File:** [`./scripts/migrate_sqlite_to_postgres.py:116`](./scripts/migrate_sqlite_to_postgres.py#L116)
- **Rule ID:** `B608` (hardcoded_sql_expressions)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b608_hardcoded_sql_expressions.html)

```python
115     )
116     source_cursor = source.execute(f'SELECT * FROM "{table}"')
117     copied = 0
```

### 22. [⚠️ MEDIUM] Possible binding to all interfaces.
- **File:** [`./scripts/proc_runner.py:120`](./scripts/proc_runner.py#L120)
- **Rule ID:** `B104` (hardcoded_bind_all_interfaces)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b104_hardcoded_bind_all_interfaces.html)

```python
119     debug = _is_truthy(os.environ.get("FLASK_DEBUG") or os.environ.get("DEBUG"))
120     app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
121     return 0
```

### 23. [⚠️ MEDIUM] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
- **File:** [`./send_launch_emails.py:163`](./send_launch_emails.py#L163)
- **Rule ID:** `B301` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b301-pickle)

```python
162     with open(token_path, "rb") as token:
163         creds = pickle.load(token)
164
```

### 24. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:26`](./ai_utils.py#L26)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
25         return json.loads(text)
26     except Exception:
27         pass
28
```

### 25. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./ai_utils.py:40`](./ai_utils.py#L40)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
39             return json.loads(cand)
40         except Exception:
41             continue
42
```

### 26. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:50`](./ai_utils.py#L50)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
49             return json.loads(sub)
50         except Exception:
51             pass
52
```

### 27. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./ai_utils.py:60`](./ai_utils.py#L60)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
59             return json.loads(sub)
60         except Exception:
61             pass
62
```

### 28. [ℹ️ LOW] Consider possible security implications associated with pickle module.
- **File:** [`./app.py:12`](./app.py#L12)
- **Rule ID:** `B403` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b403-import-pickle)

```python
11 import os
12 import pickle
13 import random
```

### 29. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:2438`](./app.py#L2438)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
2437                     date_counts[dt_part] = date_counts.get(dt_part, 0) + 1
2438                 except Exception:
2439                     continue
2440
```

### 30. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:2995`](./app.py#L2995)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
2994                         ''', (user_id, dt['template_name'], dt['subject'], dt['body'], now_str))
2995                     except Exception:
2996                         pass
2997                 conn.commit()
```

### 31. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:3187`](./app.py#L3187)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
3186                         ))
3187                     except Exception:
3188                         pass
3189                 conn.commit()
```

### 32. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3327`](./app.py#L3327)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3326             options.add_argument('--disable-dev-shm-usage')
3327             random_user_agent = random.choice(USER_AGENTS)
3328             options.add_argument(f"user-agent={random_user_agent}")
```

### 33. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3549`](./app.py#L3549)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3548             }
3549             headers = {'User-Agent': random.choice(USER_AGENTS)}
3550             try:
```

### 34. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3552`](./app.py#L3552)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3551                 logger.info(f"[LinkedIn] Sending request to LinkedIn for job list (page {page + 1})...")
3552                 time.sleep(random.uniform(*self.request_delay))  # Dynamic delay based on scan mode
3553                 response = requests.get(base_url, params=params, headers=headers, timeout=15, proxies=proxies)
```

### 35. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3620`](./app.py#L3620)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3619                         logger.info(f"[LinkedIn] Fetching job detail page: {job['link']}")
3620                         detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
3621                         time.sleep(random.uniform(2.5, 5.5)) # Increased delay to avoid 429 errors
```

### 36. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3621`](./app.py#L3621)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3620                         detail_headers = {'User-Agent': random.choice(USER_AGENTS)}
3621                         time.sleep(random.uniform(2.5, 5.5)) # Increased delay to avoid 429 errors
3622                         resp = requests.get(job['link'], headers=detail_headers, timeout=15)
```

### 37. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3698`](./app.py#L3698)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3697             session.headers.update({
3698                 'User-Agent': random.choice(USER_AGENTS),
3699                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
```

### 38. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3720`](./app.py#L3720)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3719                     # Randomized delay to avoid detection
3720                     time.sleep(random.uniform(*self.request_delay))
3721
```

### 39. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3920`](./app.py#L3920)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3919             # Randomized delay
3920             time.sleep(random.uniform(1.5, 3.5))
3921
```

### 40. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:3923`](./app.py#L3923)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
3922             headers = {
3923                 'User-Agent': random.choice(USER_AGENTS),
3924                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
```

### 41. [ℹ️ LOW] Try, Except, Continue detected.
- **File:** [`./app.py:5196`](./app.py#L5196)
- **Rule ID:** `B112` (try_except_continue)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b112_try_except_continue.html)

```python
5195                                 row[rel_col-1].value = f"🔴 {val}"
5196                         except:
5197                             continue
5198                 # --- Make Links Clickable and Button Style ---
```

### 42. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:5778`](./app.py#L5778)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
5777                 logger.info(f"Cleaned up Excel report: {excel_file}.")
5778             except Exception:
5779                 pass
5780
```

### 43. [ℹ️ LOW] Possible hardcoded password: 'token.pickle'
- **File:** [`./app.py:6107`](./app.py#L6107)
- **Rule ID:** `B105` (hardcoded_password_string)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b105_hardcoded_password_string.html)

```python
6106     """Send a MIME message via existing non-interactive Gmail OAuth credentials."""
6107     token_path = 'token.pickle'
6108     if not os.path.exists(token_path):
```

### 44. [ℹ️ LOW] Possible hardcoded password: 'https://oauth2.googleapis.com/token'
- **File:** [`./app.py:6840`](./app.py#L6840)
- **Rule ID:** `B105` (hardcoded_password_string)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b105_hardcoded_password_string.html)

```python
6839             'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
6840             'token_uri': 'https://oauth2.googleapis.com/token',
6841             'redirect_uris': [callback_uri],
6842         }
6843     }
6844     flow = Flow.from_client_config(
6845         client_config,
6846         scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email'],
6847         state=state,
```

### 45. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:7372`](./app.py#L7372)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
7371                         experience_summary = f"experience as {role}" + (f" at {comp}" if comp else "")
7372             except Exception:
7373                 pass
7374
```

### 46. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:8501`](./app.py#L8501)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
8500         conn.close()
8501     except Exception as e:
8502         pass
8503
```

### 47. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:8867`](./app.py#L8867)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
8866     fake_analysis_data = {
8867         "monthly_visits": f"{random.randint(50, 500)}K",
8868         "bounce_rate": f"{random.randint(30, 70)}%",
```

### 48. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:8868`](./app.py#L8868)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
8867         "monthly_visits": f"{random.randint(50, 500)}K",
8868         "bounce_rate": f"{random.randint(30, 70)}%",
8869         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
```

### 49. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./app.py:8869`](./app.py#L8869)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
8868         "bounce_rate": f"{random.randint(30, 70)}%",
8869         "pages_per_visit": f"{random.uniform(1.5, 5.0):.2f}",
8870     }
```

### 50. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:9407`](./app.py#L9407)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
9406                 db.update_job_status_and_notes(job_id, current_user.id, 'applied', notes or 'Applied directly via JobSnap')
9407             except Exception:
9408                 pass
9409             return jsonify({
```

### 51. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./app.py:10361`](./app.py#L10361)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
10360                 user_name = user_details.get('full_name')
10361         except: pass
10362
```

### 52. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./outreach_scraper.py:48`](./outreach_scraper.py#L48)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
47         self.session = requests.Session()
48         self.session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
49         self.scraped_domains = set()
```

### 53. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
- **File:** [`./outreach_scraper.py:108`](./outreach_scraper.py#L108)
- **Rule ID:** `B311` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b311-random)

```python
107         # Add random delay to appear more human
108         time.sleep(random.uniform(self.min_delay, self.max_delay))
109
```

### 54. [ℹ️ LOW] Consider possible security implications associated with the subprocess module.
- **File:** [`./scripts/proc_runner.py:14`](./scripts/proc_runner.py#L14)
- **Rule ID:** `B404` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess)

```python
13 import os
14 import subprocess
15 import sys
```

### 55. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:293`](./scripts/proc_runner.py#L293)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
292             sys.stderr.flush()
293         except Exception:
294             pass
295         if job_handle:
```

### 56. [ℹ️ LOW] Starting a process with a partial executable path
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

### 57. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
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

### 58. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:306`](./scripts/proc_runner.py#L306)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
305                 )
306             except Exception:
307                 pass
308             try:
```

### 59. [ℹ️ LOW] Try, Except, Pass detected.
- **File:** [`./scripts/proc_runner.py:310`](./scripts/proc_runner.py#L310)
- **Rule ID:** `B110` (try_except_pass)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

```python
309                 proc.kill()
310             except Exception:
311                 pass
312         os._exit(0)
```

### 60. [ℹ️ LOW] subprocess call - check for execution of untrusted input.
- **File:** [`./scripts/proc_runner.py:332`](./scripts/proc_runner.py#L332)
- **Rule ID:** `B603` (subprocess_without_shell_equals_true)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

```python
331 
332         proc = subprocess.Popen(cmd, env=env, cwd=str(REPO_ROOT))
333         if child_job is not None:
```

### 61. [ℹ️ LOW] Starting a process without a shell.
- **File:** [`./scripts/proc_runner.py:398`](./scripts/proc_runner.py#L398)
- **Rule ID:** `B606` (start_process_with_no_shell)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b606_start_process_with_no_shell.html)

```python
397         os.chdir(REPO_ROOT)
398         os.execvpe(cmd[0], cmd, env)
399
```

### 62. [ℹ️ LOW] Consider possible security implications associated with pickle module.
- **File:** [`./send_launch_emails.py:12`](./send_launch_emails.py#L12)
- **Rule ID:** `B403` (blacklist)
- **Advisory:** [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b403-import-pickle)

```python
11 import base64
12 import pickle
13 import argparse
```

### 63. [ℹ️ LOW] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
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
